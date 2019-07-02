import os
import tempfile
import nose.tools as nt

from ...extension.application import ExtensionApp


class TestExtensionApp(ExtensionApp):
    extension_name = 'mock'

    @classmethod
    def mock_instance(cls):
        # Return an extensionapp that already 
        # has a server initialized.
        self = cls()
        server = self.initialize_server()
        self.serverapp = server
        return self


def test_initialize():
    extension = TestExtensionApp()
    nt.assert_equal(extension.static_paths, [])
    nt.assert_equal(extension.template_paths, [])
    nt.assert_equal(extension.settings, {})
    nt.assert_equal(extension.handlers, [])


def test_initialize_from_argv():
    extension = TestExtensionApp(static_paths=['test'])
    nt.assert_in('test', extension.static_paths)


def test_initialize_server():
    argv = [
        '--ServerApp.open_browser=False'
    ]
    extension = TestExtensionApp()
    server = extension.initialize_server(argv=argv)
    nt.assert_equal(server.open_browser, False)


def test_prepare_config():
    extension = TestExtensionApp.mock_instance()
    extension._prepare_config()
    nt.assert_in('mock_config', extension.settings)


def test_prepare_settings():
    extension = TestExtensionApp.mock_instance()
    extension._prepare_settings()
    nt.assert_in('mock_static_paths', extension.settings)

  
def test_prepare_launch():
    extension = TestExtensionApp._prepare_launch()
    nt.assert_true(isinstance(extension, ExtensionApp))
    nt.assert_true(hasattr(extension, 'serverapp'))


def test_mixed_initialization():
    # Build multiple arguments.
    argv = [
        '--ServerApp.open_browser=False',
        '--TestExtensionApp.static_paths=["test"]'
    ]
    extension = TestExtensionApp._prepare_launch(argv=argv)
    nt.assert_equal(extension.serverapp.open_browser, False)
    nt.assert_in('test', extension.static_paths)
