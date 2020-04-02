import pytest


@pytest.fixture
def server_config(template_dir):
    return {
        "ServerApp": {
            "jpserver_extensions": {
                "tests.extension.mockextensions": True
            }
        },
        "MockExtensionApp": {
            "template_paths": [
                str(template_dir)
            ]
        }
    }


async def test_handler(fetch):
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'mock trait'


async def test_handler_template(fetch):
    r = await fetch(
        'mock_template',
        method='GET'
    )
    assert r.code == 200


async def test_handler_setting(fetch, serverapp):
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
