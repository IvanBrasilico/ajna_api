# Tescases for virasana.app.py
import json

from tests.base_api_test import ApiTestCase


class ApiLoginTestCase(ApiTestCase):

    def test_json_requerido(self):
        self._case(status_code=400, msg='JSON requerido')

    def test_usuario_obrigatorio(self):
        self._case(pjson={'dummy': 'dummy'},
                   status_code=400,
                   msg='Parametro username requerido')

    def test_password_obrigatorio(self):
        self._case(pjson={'username': 'ivan'},
                   status_code=400,
                   msg='Parametro password requerido')

    def test_login_invalido(self):
        self._case(pjson={'username': 'ivan', 'password': 'ivan'},
                   status_code=401)

    def test_login_ok(self):
        self._case(pjson={'username': 'ajna', 'password': 'ajna'},
                   status_code=200)

    def test_unauthorized(self):
        rv = self.client.get('api/test')
        assert rv.status_code == 401

    def test_login_access_test(self):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': 'ajna', 'password': 'ajna'}),
            content_type='application/json')
        token = rv.json.get('access_token')
        headers = {'Authorization': 'Bearer ' + token}
        rv = self.client.get('api/test', headers=headers)
        assert rv.status_code == 200

    def test_logout_unauthorized(self):
        rv = self.client.post(
            '/api/login',
            data=json.dumps({'username': 'ajna', 'password': 'ajna'}),
            content_type='application/json')
        print(rv)
        print(rv.data)
        token = rv.json.get('access_token')
        headers = {'Authorization': 'Bearer ' + token}
        rv = self.client.get('api/test', headers=headers)
        assert rv.status_code == 200
        rv = self.client.delete('api/logout', headers=headers)
        print(rv)
        assert rv.json.get('msg') == 'Logout efetuado'
        rv = self.client.get('api/test', headers=headers)
        assert rv.status_code == 401
