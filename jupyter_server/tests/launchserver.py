"""Base class for server tests."""

from binascii import hexlify
from contextlib import contextmanager
import errno
import os
import sys
from threading import Thread, Event
import time
from unittest import TestCase

from unittest.mock import patch

import requests
from tornado.ioloop import IOLoop
import zmq

import jupyter_core.paths
from traitlets.config import Config
from ..serverapp import ServerApp
from ..utils import url_path_join
from tempfile import TemporaryDirectory

MAX_WAITTIME = 30   # seconds to wait for Jupyter server to start
POLL_INTERVAL = 0.1  # time between attempts


# TimeoutError is a builtin on Python 3. This can be removed when we stop
# supporting Python 2.
class TimeoutError(Exception):
    pass


class ServerTestBase(TestCase):
    """A base class for tests that need a running Jupyter server.

    This create some empty config and runtime directories
    and then starts the Jupyter server with them.
    """

    port = 12341
    config = None
    # run with a base URL that would be escaped,
    # to test that we don't double-escape URLs
    url_prefix = '/a%40b/'

    @classmethod
    def wait_until_alive(cls):
        """Wait for the server to be alive"""
        url = cls.base_url() + 'api/contents'
        for _ in range(int(MAX_WAITTIME / POLL_INTERVAL)):
            try:
                requests.get(url)
            except Exception as e:
                if not cls.server_thread.is_alive():
                    raise RuntimeError("The Jupyter server failed to start")
                time.sleep(POLL_INTERVAL)
            else:
                return

        raise TimeoutError("The Jupyter server didn't start up correctly.")

    @classmethod
    def wait_until_dead(cls):
        """Wait for the server process to terminate after shutdown"""
        cls.server_thread.join(timeout=MAX_WAITTIME)
        if cls.server_thread.is_alive():
            raise TimeoutError("Undead Jupyter server")

    @classmethod
    def auth_headers(cls):
        headers = {}
        if cls.token:
            headers['Authorization'] = 'token %s' % cls.token
        return headers

    @classmethod
    def request(cls, verb, path, **kwargs):
        """Send a request to my server

        with authentication and everything.
        """
        headers = kwargs.setdefault('headers', {})
        headers.update(cls.auth_headers())
        response = requests.request(verb,
            url_path_join(cls.base_url(), path),
            **kwargs)
        return response

    @classmethod
    def setup_class(cls):
        cls.tmp_dir = TemporaryDirectory()

        def tmp(*parts):
            path = os.path.join(cls.tmp_dir.name, *parts)
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            return path

        cls.home_dir = tmp('home')
        data_dir = cls.data_dir = tmp('data')
        config_dir = cls.config_dir = tmp('config')
        runtime_dir = cls.runtime_dir = tmp('runtime')
        cls.root_dir = tmp('root_dir')
        cls.env_patch = patch.dict('os.environ', {
            'HOME': cls.home_dir,
            'PYTHONPATH': os.pathsep.join(sys.path),
            'JUPYTER_NO_CONFIG': '1',  # needed in the future
            'JUPYTER_CONFIG_DIR': config_dir,
            'JUPYTER_DATA_DIR': data_dir,
            'JUPYTER_RUNTIME_DIR': runtime_dir,
        })
        cls.env_patch.start()
        cls.path_patch = patch.multiple(
            jupyter_core.paths,
            SYSTEM_JUPYTER_PATH=[tmp('share', 'jupyter')],
            ENV_JUPYTER_PATH=[tmp('env', 'share', 'jupyter')],
            SYSTEM_CONFIG_PATH=[tmp('etc', 'jupyter')],
            ENV_CONFIG_PATH=[tmp('env', 'etc', 'jupyter')],
        )
        cls.path_patch.start()

        config = cls.config or Config()
        config.NotebookNotary.db_file = ':memory:'

        cls.token = hexlify(os.urandom(4)).decode('ascii')

        started = Event()

        def start_thread():
            if 'asyncio' in sys.modules:
                import asyncio
                asyncio.set_event_loop(asyncio.new_event_loop())
            app = cls.server = ServerApp(
                port=cls.port,
                port_retries=0,
                open_browser=False,
                config_dir=cls.config_dir,
                data_dir=cls.data_dir,
                runtime_dir=cls.runtime_dir,
                root_dir=cls.root_dir,
                base_url=cls.url_prefix,
                config=config,
                allow_root=True,
                token=cls.token,
            )
            # don't register signal handler during tests
            app.init_signal = lambda: None
            # clear log handlers and propagate to root for pytest to capture it
            # needs to be redone after initialize, which reconfigures logging
            app.log.propagate = True
            app.log.handlers = []
            app.initialize(argv=[])
            app.log.propagate = True
            app.log.handlers = []
            loop = IOLoop.current()
            loop.add_callback(started.set)
            try:
                app.start()
            finally:
                # set the event, so failure to start doesn't cause a hang
                started.set()
                app.session_manager.close()
        cls.server_thread = Thread(target=start_thread)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        started.wait()
        cls.wait_until_alive()

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        cls.wait_until_dead()
        cls.env_patch.stop()
        cls.path_patch.stop()
        cls.tmp_dir.cleanup()

        # cleanup global zmq Context, to ensure we aren't leaving dangling sockets
        def cleanup_zmq():
            zmq.Context.instance().term()
        t = Thread(target=cleanup_zmq)
        t.daemon = True
        t.start()
        t.join(5)  # give it a few seconds to clean up (this should be immediate)
        # if term never returned, there's zmq stuff still open somewhere, so shout about it.
        if t.is_alive():
            raise RuntimeError("Failed to teardown zmq Context, open sockets likely left lying around.")

    @classmethod
    def base_url(cls):
        return 'http://localhost:%i%s' % (cls.port, cls.url_prefix)


@contextmanager
def assert_http_error(status, msg=None):
    try:
        yield
    except requests.HTTPError as e:
        real_status = e.response.status_code
        assert real_status == status, \
                    "Expected status %d, got %d" % (status, real_status)
        if msg:
            assert msg in str(e), e
    else:
        assert False, "Expected HTTP error status"
