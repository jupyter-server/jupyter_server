"""Test the basic /api endpoints"""

from jupyter_server._tz import isoformat
from jupyter_server.utils import url_path_join
from jupyter_server.tests.launchserver import ServerTestBase


class KernelAPITest(ServerTestBase):
    """Test the kernels web service API"""

    def _req(self, verb, path, **kwargs):
        r = self.request(verb, url_path_join('api', path))
        r.raise_for_status()
        return r

    def get(self, path, **kwargs):
        return self._req('GET', path)

    def test_get_spec(self):
        r = self.get('spec.yaml')
        assert r.text

    def test_get_status(self):
        r = self.get('status')
        data = r.json()
        assert data['connections'] == 0
        assert data['kernels'] == 0
        assert data['last_activity'].endswith('Z')
        assert data['started'].endswith('Z')
        assert data['started'] == isoformat(self.server.web_app.settings['started'])
