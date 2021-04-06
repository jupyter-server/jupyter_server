"""Test launching Jupyter Server Applications
through as ExtensionApp launch_instance.
"""
from pathlib import Path
import os
import sys
import time
import pytest
import subprocess
import requests
from binascii import hexlify


HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def port():
    return 9999


@pytest.fixture
def token():
    return hexlify(os.urandom(4)).decode("ascii")


@pytest.fixture
def auth_header(token):
    return {
        'Authorization': 'token %s' % token
    }


def wait_up(url, interval=0.1, check=None):
    while True:
        try:
            r = requests.get(url)
        except Exception:
            if check:
                assert check()
            #print("waiting for %s" % url)
            time.sleep(interval)
        else:
            break


@pytest.fixture
def launch_instance(request, port, token):
    def _run_in_subprocess(argv=[], add_token=True):

        def _kill_extension_app():
            try:
                process.terminate()
            except OSError:
                # Already dead.
                pass
            process.wait(10)

        if add_token:
            f'--ServerApp.token="{token}"',

        process = subprocess.Popen([
            sys.executable, '-m',
            'mockextensions.app',
            f'--port={port}',
            '--ip=127.0.0.1',
            '--no-browser',
            *argv,
        ], cwd=HERE)

        request.addfinalizer(_kill_extension_app)
        url = f'http://127.0.0.1:{port}'
        wait_up(url, check=lambda: process.poll() is None)
        return process

    return _run_in_subprocess


@pytest.fixture
def fetch(port, auth_header):
    def _get(endpoint):
        url = f"http://127.0.0.1:{port}" + endpoint
        return requests.get(url, headers=auth_header)
    return _get


def test_launch_instance(launch_instance, fetch):
    launch_instance()
    r = fetch('/mock')
    assert r.status_code == 200


def test_base_url(launch_instance, fetch):
    launch_instance(['--ServerApp.base_url=/foo'])
    r = fetch("/foo/mock")
    assert r.status_code == 200


def test_token_file(launch_instance, fetch, token):
    token_file = HERE / Path('token_file.txt')
    os.environ['JUPYTER_TOKEN_FILE'] = str(token_file)
    token_file.write_text(token, encoding='utf-8')

    launch_instance(add_token=False)
    r = fetch("/mock")
    del os.environ['JUPYTER_TOKEN_FILE']
    token_file.unlink()
    assert r.status_code == 200


