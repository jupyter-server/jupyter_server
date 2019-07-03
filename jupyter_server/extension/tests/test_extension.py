import os
import tempfile
import nose.tools as nt

from ...extension.application import ExtensionApp
from ...serverapp import ServerApp


class MockExtension(ExtensionApp):
    extension_name = 'mock'        


class ExtensionTestingMixin:

    port = 12341

    def server_kwargs(self):
        return dict(
            port=self.port,
            port_retries=0,
            open_browser=False,
            allow_root=True
        )

    def tearDown(self):
        #self.serverapp.stop()
        self.serverapp.http_server.stop()
        self.serverapp.clear_instance()

class TestExtensionAppInitialize(ExtensionTestingMixin):

    def setUp(self):
        self.serverapp = ServerApp(**self.server_kwargs())
        self.serverapp.init_signal = lambda : None
        self.serverapp.init_terminals = lambda : None
        # clear log handlers and propagate to root for nose to capture it
        # needs to be redone after initialize, which reconfigures logging
        self.serverapp.log.propagate = True
        self.serverapp.log.handlers = []
        self.serverapp.initialize(argv=[])

    def test_instance_creation(self):
        self.extension = MockExtension()
        extension = self.extension
        nt.assert_equal(extension.static_paths, [])
        nt.assert_equal(extension.template_paths, [])
        nt.assert_equal(extension.settings, {})
        nt.assert_equal(extension.handlers, [])

    def test_instance_creation_with_arg(self):
        self.extension = MockExtension(static_paths=['test'])
        nt.assert_in('test', self.extension.static_paths)

    def test_initialize(self):
        self.extension = MockExtension()
        self.extension.initialize(self.serverapp)
        nt.assert_true(isinstance(self.extension.serverapp, ServerApp))


class TestExtensionServerInitialize(ExtensionTestingMixin):

    def test_initialize_server(self):
        self.extension = MockExtension()
        self.serverapp = self.extension.initialize_server(**self.server_kwargs())
        nt.assert_true(isinstance(self.serverapp, ServerApp))

    def test_initialize_server_argv(self):
        argv = [
            '--ServerApp.tornado_settings={"test":"hello world"}'
        ]
        self.extension = MockExtension()
        self.serverapp = self.extension.initialize_server(
            argv=argv, **self.server_kwargs())

        nt.assert_in("test", self.serverapp.tornado_settings)

    def test_initialize_mixed_argv(self):
        argv = [
            '--ServerApp.tornado_settings={"test":"hello world"}',
            '--MockExtension.static_paths=["test"]'
        ]
        # Initialize server
        self.extension = MockExtension()
        self.serverapp = self.extension.initialize_server(
            argv=argv,
            **self.server_kwargs()
        )
        self.extension.initialize(self.serverapp, argv=argv)
        nt.assert_in("test", self.serverapp.tornado_settings)
        nt.assert_in("test", self.extension.static_paths)

