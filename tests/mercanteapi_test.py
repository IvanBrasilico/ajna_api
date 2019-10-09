# Tescases for mercanteapi blueprint
import json
from sqlalchemy import create_engine
from integracao.mercantealchemy import t_conhecimentosEmbarque

from tests.base_api_test import ApiTestCase


class MercanteApiTestCase(ApiTestCase):

    def setUp(self):
        super().setUp()
        self.engine = create_engine('sqlite:///:memory:/')

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_conhecimentosEmbarque(self):
        self.unauthorized('/api/conhecimentosEmbarque')
        self.unauthorized('/api/conhecimentosEmbarque&numeroCEmercante=0')
        self.unauthorized('/api/conhecimentosEmbarque/0')
        self.unauthorized('/api/conhecimentosEmbarque/new/0')

    def test_invalid_login_grid_data(self):
        self.invalid_login('/api/conhecimentosEmbarque')
        self.invalid_login('/api/conhecimentosEmbarque&numeroCEmercante=0')
        self.invalid_login('/api/conhecimentosEmbarque/0')
        self.invalid_login('/api/conhecimentosEmbarque/new/0')

    def test_not_allowed_data(self):
        self.not_allowed('/api/conhecimentosEmbarque')
        self.not_allowed('/api/conhecimentosEmbarque&numeroCEmercante=0')
        self.not_allowed('/api/conhecimentosEmbarque/0')
        self.not_allowed('/api/conhecimentosEmbarque/new/0')

    def test_grid_data_get(self):
        self.login()
        self._case('GET', '/api/conhecimentosEmbarque/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        with self.engine.begin() as conn:
            ins = t_conhecimentosEmbarque.insert()
            conn.execute(ins, {'numeroCEmercante': '000'})
        r = self._case('GET', '/api/conhecimentosEmbarque/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
