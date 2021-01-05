import os
import pytest


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.script_launch_mode('subprocess')


def test_server_extension_list(jp_environ, script_runner):
    ret = script_runner.run(
        'jupyter',
        'server',
        'extension',
        'list',
    )
    assert ret.success