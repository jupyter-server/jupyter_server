import pytest

from jupyter_core import paths
from jupyter_server.extension import serverextension

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.script_launch_mode('subprocess')


def test_server_extension_list(environ, script_runner):
    ret = script_runner.run('jupyter', 'server', 'extension', 'list')
    assert ret.success


def test_server_extension_enable(environ, inject_mock_extension, script_runner):
    # 'mock' is not a valid extension The entry point should complete
    # but print to sterr.
    inject_mock_extension()
    extension_name = 'mockextension'
    ret = script_runner.run('jupyter', 'server', 'extension', 'enable', extension_name)
    assert ret.success
    assert 'Enabling: {}'.format(extension_name) in ret.stderr


def test_server_extension_disable(environ, script_runner):
    # 'mock' is not a valid extension The entry point should complete
    # but print to sterr.
    extension_name = 'mockextension'
    ret = script_runner.run('jupyter', 'server', 'extension', 'disable', extension_name)
    assert ret.success
    assert 'Disabling: {}'.format(extension_name) in ret.stderr
