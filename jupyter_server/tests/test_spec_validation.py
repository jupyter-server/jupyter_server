import json
import logging
import os
from binascii import hexlify

import pytest
from tornado.httpclient import HTTPClientError
from traitlets.config import Config
from jupyter_server.serverapp import ServerApp


pytest.importorskip("tornado_openapi3")


@pytest.fixture(scope="function")
def jp_serverapp(
    jp_ensure_app_fixture,
    jp_server_config,
    jp_argv,
    jp_nbconvert_templates,  # this fixture must preceed jp_environ
    jp_environ,
    jp_http_port,
    jp_base_url,
    tmp_path,
    jp_root_dir,
    io_loop,
    jp_logging_stream,
):
    """Starts a Jupyter Server instance with endpoint specifications based on the established configuration values.

    It overrides the default fixture to define a server with spec validation.
    """

    class ServerAppWithSpec(ServerApp):
        _allowed_spec = {
            "openapi": "3.0.1",
            "info": {"title": "Test specs", "version": "0.0.1"},
            "paths": {
                "/api/contents/{path}": {
                    # Will be blocked by _blocked_spec
                    "get": {
                        "parameters": [
                            {
                                "name": "path",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
                "/api/contents/{path}/checkpoints": {
                    "post": {
                        "parameters": [
                            {
                                "name": "path",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"201": {"description": ""}},
                    },
                },
                "/api/sessions/{sessionId}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "sessionId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
            },
        }
        
        _blocked_spec = {
            "openapi": "3.0.1",
            "info": {"title": "Test specs", "version": "0.0.1"},
            "paths": {
                "/api/contents/{path}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "path",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
            },
        }

        _slash_encoder = (
            r"/api/contents/([^/?]+(?:(?:/[^/]+)*?))/checkpoints$",
            r"/api/contents/([^/?]+(?:(?:/[^/]+)*?))$",
            # Test regex without group match
            r"/api/sessions",
        )

    ServerAppWithSpec.clear_instance()

    def _configurable_serverapp(
        config=jp_server_config,
        base_url=jp_base_url,
        argv=jp_argv,
        environ=jp_environ,
        http_port=jp_http_port,
        tmp_path=tmp_path,
        root_dir=jp_root_dir,
        **kwargs
    ):
        c = Config(config)
        c.NotebookNotary.db_file = ":memory:"
        token = hexlify(os.urandom(4)).decode("ascii")
        app = ServerAppWithSpec.instance(
            # Set the log level to debug for testing purposes
            log_level="DEBUG",
            port=http_port,
            port_retries=0,
            open_browser=False,
            root_dir=str(root_dir),
            base_url=base_url,
            config=c,
            allow_root=True,
            token=token,
            **kwargs
        )

        app.init_signal = lambda: None
        app.log.propagate = True
        app.log.handlers = []
        # Initialize app without httpserver
        app.initialize(argv=argv, new_httpserver=False)
        # Reroute all logging StreamHandlers away from stdin/stdout since pytest hijacks
        # these streams and closes them at unfortunate times.
        stream_handlers = [
            h for h in app.log.handlers if isinstance(h, logging.StreamHandler)
        ]
        for handler in stream_handlers:
            handler.setStream(jp_logging_stream)
        app.log.propagate = True
        app.log.handlers = []
        # Start app without ioloop
        app.start_app()
        return app

    app = _configurable_serverapp(config=jp_server_config, argv=jp_argv)
    yield app
    app.remove_server_info_file()
    app.remove_browser_open_files()


async def test_ServerApp_with_spec_validation_blocked(
    tmp_path, jp_serverapp, jp_fetch
):
    content = tmp_path / jp_serverapp.root_dir / "content" / "test.txt"
    content.parent.mkdir(parents=True)
    content.write_text("dummy content")

    with pytest.raises(HTTPClientError) as error:
        await jp_fetch(
            "api",
            "contents",
            content.parent.name,
            content.name,
            method="GET",
        )

    assert error.value.code == 403


async def test_ServerApp_with_spec_validation_not_allowed(
    tmp_path, jp_serverapp, jp_fetch
):
    content = tmp_path / jp_serverapp.root_dir / "content" / "test.txt"
    content.parent.mkdir(parents=True)
    content.write_text("dummy content")

    with pytest.raises(HTTPClientError) as error:
        await jp_fetch(
            "api",
            "contents",
            content.parent.name,
            content.name,
            method="PUT",
            body=b"{}"
        )

    assert error.value.code == 403


async def test_ServerApp_with_spec_validation_allowed_with_encoded_path(
    tmp_path, jp_serverapp, jp_fetch
):
    content = tmp_path / jp_serverapp.root_dir / "content" / "test.txt"
    content.parent.mkdir(parents=True)
    content.write_text("dummy content")

    # Create a checkpoint
    r = await jp_fetch(
        "api",
        "contents",
        content.parent.name,
        content.name,
        "checkpoints",
        method="POST",
        allow_nonstandard_methods=True,
    )

    assert r.code == 201
    cp1 = json.loads(r.body.decode())
    assert set(cp1) == {"id", "last_modified"}
    assert r.headers["Location"].split("/")[-1] == cp1["id"]
