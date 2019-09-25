"""Test the kernels service API."""

import json
import time

from traitlets.config import Config

from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

from jupyter_client.kernelspec import NATIVE_KERNEL_NAME

from jupyter_server.utils import url_path_join
from jupyter_server.tests.launchserver import ServerTestBase, assert_http_error



class KernelAPI(object):
    """Wrapper for kernel REST API requests"""
    def __init__(self, request, base_url, headers):
        self.request = request
        self.base_url = base_url
        self.headers = headers

    def _req(self, verb, path, body=None):
        response = self.request(verb,
                url_path_join('api/kernels', path), data=body)

        if 400 <= response.status_code < 600:
            try:
                response.reason = response.json()['message']
            except:
                pass
        response.raise_for_status()

        return response

    def list(self):
        return self._req('GET', '')

    def get(self, id):
        return self._req('GET', id)

    def start(self, name=NATIVE_KERNEL_NAME):
        body = json.dumps({'name': name})
        return self._req('POST', '', body)

    def shutdown(self, id):
        return self._req('DELETE', id)

    def interrupt(self, id):
        return self._req('POST', url_path_join(id, 'interrupt'))

    def restart(self, id):
        return self._req('POST', url_path_join(id, 'restart'))

    def websocket(self, id):
        loop = IOLoop()
        loop.make_current()
        req = HTTPRequest(
            url_path_join(self.base_url.replace('http', 'ws', 1), 'api/kernels', id, 'channels'),
            headers=self.headers,
        )
        f = websocket_connect(req)
        return loop.run_sync(lambda : f)


class KernelAPITest(ServerTestBase):
    """Test the kernels web service API"""
    def setUp(self):
        self.kern_api = KernelAPI(self.request,
                                  base_url=self.base_url(),
                                  headers=self.auth_headers(),
                                  )

    def tearDown(self):
        for k in self.kern_api.list().json():
            self.kern_api.shutdown(k['id'])

    def test_no_kernels(self):
        """Make sure there are no kernels running at the start"""
        kernels = self.kern_api.list().json()
        self.assertEqual(kernels, [])

    def test_default_kernel(self):
        # POST request
        r = self.kern_api._req('POST', '')
        kern1 = r.json()
        self.assertEqual(r.headers['location'], url_path_join(self.url_prefix, 'api/kernels', kern1['id']))
        self.assertEqual(r.status_code, 201)
        self.assertIsInstance(kern1, dict)

        report_uri = url_path_join(self.url_prefix, 'api/security/csp-report')
        expected_csp = '; '.join([
            "frame-ancestors 'self'",
            'report-uri ' + report_uri,
            "default-src 'none'"
        ])
        self.assertEqual(r.headers['Content-Security-Policy'], expected_csp)

    def test_main_kernel_handler(self):
        # POST request
        r = self.kern_api.start()
        kern1 = r.json()
        self.assertEqual(r.headers['location'], url_path_join(self.url_prefix, 'api/kernels', kern1['id']))
        self.assertEqual(r.status_code, 201)
        self.assertIsInstance(kern1, dict)

        report_uri = url_path_join(self.url_prefix, 'api/security/csp-report')
        expected_csp = '; '.join([
            "frame-ancestors 'self'",
            'report-uri ' + report_uri,
            "default-src 'none'"
        ])
        self.assertEqual(r.headers['Content-Security-Policy'], expected_csp)

        # GET request
        r = self.kern_api.list()
        self.assertEqual(r.status_code, 200)
        assert isinstance(r.json(), list)
        self.assertEqual(r.json()[0]['id'], kern1['id'])
        self.assertEqual(r.json()[0]['name'], kern1['name'])

        # create another kernel and check that they both are added to the
        # list of kernels from a GET request
        kern2 = self.kern_api.start().json()
        assert isinstance(kern2, dict)
        r = self.kern_api.list()
        kernels = r.json()
        self.assertEqual(r.status_code, 200)
        assert isinstance(kernels, list)
        self.assertEqual(len(kernels), 2)

        # Interrupt a kernel
        r = self.kern_api.interrupt(kern2['id'])
        self.assertEqual(r.status_code, 204)

        # Restart a kernel
        r = self.kern_api.restart(kern2['id'])
        rekern = r.json()
        self.assertEqual(rekern['id'], kern2['id'])
        self.assertEqual(rekern['name'], kern2['name'])

    def test_kernel_handler(self):
        # GET kernel with given id
        kid = self.kern_api.start().json()['id']
        r = self.kern_api.get(kid)
        kern1 = r.json()
        self.assertEqual(r.status_code, 200)
        assert isinstance(kern1, dict)
        self.assertIn('id', kern1)
        self.assertEqual(kern1['id'], kid)

        # Request a bad kernel id and check that a JSON
        # message is returned!
        bad_id = '111-111-111-111-111'
        with assert_http_error(404, 'Kernel does not exist: ' + bad_id):
            self.kern_api.get(bad_id)

        # DELETE kernel with id
        r = self.kern_api.shutdown(kid)
        self.assertEqual(r.status_code, 204)
        kernels = self.kern_api.list().json()
        self.assertEqual(kernels, [])

        # Request to delete a non-existent kernel id
        bad_id = '111-111-111-111-111'
        with assert_http_error(404, 'Kernel does not exist: ' + bad_id):
            self.kern_api.shutdown(bad_id)

    def test_connections(self):
        kid = self.kern_api.start().json()['id']
        model = self.kern_api.get(kid).json()
        self.assertEqual(model['connections'], 0)

        ws = self.kern_api.websocket(kid)
        model = self.kern_api.get(kid).json()
        self.assertEqual(model['connections'], 1)
        ws.close()
        # give it some time to close on the other side:
        for i in range(10):
            model = self.kern_api.get(kid).json()
            if model['connections'] > 0:
                time.sleep(0.1)
            else:
                break
        model = self.kern_api.get(kid).json()
        self.assertEqual(model['connections'], 0)


class KernelFilterTest(ServerTestBase):
    # A special install of ServerTestBase where only `kernel_info_request`
    # messages are allowed.

    config = Config({
        'ServerApp': {
            'MappingKernelManager': {
                'allowed_message_types': ['kernel_info_request']
            }
        }
    })

    # Sanity check verifying that the configurable was properly set.
    def test_config(self):
        self.assertEqual(self.server.kernel_manager.allowed_message_types, ['kernel_info_request'])
