"""Tests for authorization"""
import asyncio
import json
import os

from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from tornado.httpclient import HTTPClientError
from tornado.util import TimeoutError

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.services.security import csp_report_uri


async def test_api_contents_path_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_contents_path_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_contents_path_patch(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                method="PATCH",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 400
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_contents_path_put(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                method="PUT",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_contents_path_delete(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                method="DELETE",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_contents_checkpoints_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                "checkpoints",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_contents_checkpoints_post(jp_fetch, jp_root_dir):
    open(os.path.join(jp_root_dir, "foo"), "wt").close()
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                "checkpoints",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_contents_modifycheckpoints_post(jp_fetch, jp_root_dir):
    os.makedirs(os.path.join(jp_root_dir, ".ipynb_checkpoints"), exist_ok=True)
    open(os.path.join(jp_root_dir, ".ipynb_checkpoints", "foo-bar"), "wt").close()
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                "checkpoints",
                "bar",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_contents_modifycheckpoints_delete(jp_fetch, jp_root_dir):
    os.makedirs(os.path.join(jp_root_dir, ".ipynb_checkpoints"), exist_ok=True)
    open(os.path.join(jp_root_dir, ".ipynb_checkpoints", "foo-bar"), "wt").close()
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo",
                "checkpoints",
                "bar",
                method="DELETE",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_contents_trustnotebook_post(jp_fetch, jp_root_dir):
    with open(os.path.join(jp_root_dir, "foo.ipynb"), "wt") as f:
        f.write('{"metadata": {}, "nbformat": 4, "nbformat_minor": 5, "cells": []}')
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "contents"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "contents",
                "foo.ipynb",
                "trust",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_kernels_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_kernels_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_kernels_kernelid_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                "a-b-c-d-e",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_kernels_kernelid_delete(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                "a-b-c-d-e",
                method="DELETE",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_kernels_kernelid_interrupt_post(jp_fetch):
    # TODO: start a kernel
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                "a-b-c-d-e",
                "interrupt",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_kernels_kernelid_restart_post(jp_fetch):
    # TODO: start a kernel
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "kernels"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernels",
                "a-b-c-d-e",
                "restart",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 500
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_kernelspecs_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernelspecs"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "kernelspecs",
                "foo",
                "bar",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_kernelspecs_head(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernelspecs"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "kernelspecs",
                "foo",
                "bar",
                method="HEAD",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_kernelspecs_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernelspecs"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernelspecs",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_kernelspecs_kernelname_get(jp_fetch):
    # TODO: write a kernelspecs
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "kernelspecs"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "kernelspecs",
                "foo",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_api_nbconvert_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "nbconvert"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "nbconvert",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_nbconvert_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "nbconvert"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "nbconvert",
                "pdf",
                "foo",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert False, "Should raise HTTPClientError"


async def test_nbconvert_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "nbconvert"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "nbconvert",
                "notebook",
                method="POST",
                body='{"content": {"metadata": {}, "nbformat": 4, "nbformat_minor": 5, "cells": []}}',
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_spec_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "api"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "spec.yaml",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_status_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "api"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "status",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_config_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "config"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "config",
                "foo",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_config_put(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "config"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "config",
                "foo",
                method="PUT",
                body="{}",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_config_patch(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "config"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "config",
                "foo",
                method="PATCH",
                body="{}",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_csp_report_uri_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "csp"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                *tuple(csp_report_uri.split("/")[1:]),
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_sessions_sessionid_get(jp_fetch):
    # TODO: create a session
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "sessions"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "sessions",
                "a-b-c-d-e",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_sessions_sessionid_patch(jp_fetch):
    # TODO: create a session
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "sessions"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "sessions",
                "a-b-c-d-e",
                method="PATCH",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 400
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_sessions_sessionid_delete(jp_fetch):
    # TODO: create a session
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "sessions"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "sessions",
                "a-b-c-d-e",
                method="DELETE",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                assert e.code == 404
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_sessions_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "sessions"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "sessions",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_sessions_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "sessions"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "sessions",
                method="POST",
                body='{"path": "foo", "type": "bar"}',
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_shutdown_post(jp_fetch):
    # TODO: authorized = True
    # but cannot catch the tornado.util.TimeoutError
    for authorized in (False,):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "shutdown"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "shutdown",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except TimeoutError:
            if authorized:
                pass
            else:
                raise
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_terminalroot_get(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "terminal"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "terminals",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_terminalroot_post(jp_fetch):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "terminal"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "terminals",
                method="POST",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_terminal_get(jp_fetch):
    JupyterHandler.user_is_authorized = lambda self, user, action, resource: True
    await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "terminal"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "terminals",
                "1",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_api_terminal_delete(jp_fetch):
    JupyterHandler.user_is_authorized = lambda self, user, action, resource: True
    await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "write"
            assert resource == "terminal"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "api",
                "terminals",
                "1",
                method="DELETE",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_view_get(jp_fetch, jp_root_dir):
    open(os.path.join(jp_root_dir, "foo"), "wt").close()
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            assert action == "read"
            assert resource == "view"
            return authorized

        JupyterHandler.user_is_authorized = user_is_authorized
        try:
            await jp_fetch(
                "view",
                "foo",
                method="GET",
            )
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"


async def test_channels(jp_fetch, jp_ws_fetch, jp_http_port, jp_auth_header):
    for authorized in (True, False):

        def user_is_authorized(self, user, action, resource):
            assert user == self.get_current_user()
            if action == "execute" and resource == "channels":
                return authorized
            return True

        JupyterHandler.user_is_authorized = user_is_authorized

        r = await jp_fetch(
            "api", "kernels", method="POST", body=json.dumps({"name": NATIVE_KERNEL_NAME})
        )
        kid = json.loads(r.body.decode())["id"]

        r = await jp_fetch("api", "kernels", kid, method="GET")
        model = json.loads(r.body.decode())
        assert model["connections"] == 0

        ws = None
        try:
            ws = await jp_ws_fetch("api", "kernels", kid, "channels")
        except HTTPClientError as e:
            if authorized:
                raise
            else:
                assert e.code == 401
        else:
            assert authorized, "Should raise HTTPClientError"

        r = await jp_fetch("api", "kernels", kid, method="GET")
        model = json.loads(r.body.decode())
        if ws is None:
            assert model["connections"] == 0
        else:
            assert model["connections"] == 1
            ws.close()
            for i in range(10):
                r = await jp_fetch("api", "kernels", kid, method="GET")
                model = json.loads(r.body.decode())
                if model["connections"] > 0:
                    await asyncio.sleep(0.1)
                else:
                    break

            r = await jp_fetch("api", "kernels", kid, method="GET")
            model = json.loads(r.body.decode())
            assert model["connections"] == 0
