# Tescases for virasana.app.py
# Tescases for virasana.app.py
import json

from tests.base_api_test import ApiTestCase


class ApiLoginTestCase(ApiTestCase):

    def test_unauthorized_grid_data(self):
        self._case('GET', '/api/grid_data',
                   status_code=401,
                   msg='Missing Authorization Header')

    def test_login_access_test(self):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': 'ajna', 'password': 'ajna'}),
            content_type='application/json')
        token = rv.json.get('access_token')
        headers = {'Authorization': 'Bearer ' + token}
        rv = self.client.get('api/test', headers=headers)
        assert rv.status_code == 200
