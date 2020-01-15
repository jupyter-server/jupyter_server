import pytest

from jupyter_server.serverapp import ServerApp

# ------------------ Start tests -------------------

async def test_handler(fetch, extended_serverapp):
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'mock trait'


async def test_handler_setting(fetch, serverapp, make_mock_extension_app):
    # Configure trait in Mock Extension.
    m = make_mock_extension_app(mock_trait='test mock trait')
    m.initialize(serverapp)

    # Test that the extension trait was picked up by the webapp.
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'test mock trait'


async def test_handler_argv(fetch, serverapp, make_mock_extension_app):
    # Configure trait in Mock Extension.
    m = make_mock_extension_app()
    argv = ['--MockExtensionApp.mock_trait="test mock trait"']
    m.initialize(serverapp, argv=argv)

    # Test that the extension trait was picked up by the webapp.
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'test mock trait'
