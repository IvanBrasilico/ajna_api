# Tescases for mercanteapi blueprint
import json
from dateutil import parser
from integracao.mercantealchemy import metadata
from integracao.mercantealchemy import conhecimentos, t_conhecimentosEmbarque

from tests.base_api_test import ApiTestCase


class MercanteApiTestCase(ApiTestCase):

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_conhecimentosEmbarque(self):
        self.unauthorized('/api/conhecimentosEmbarque')
        self.unauthorized('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.unauthorized('/api/conhecimentosEmbarque/0')
        self.unauthorized('/api/conhecimentosEmbarque/new/0')
        self.unauthorized('/api/conhecimentos?numeroCEmercante=0')
        self.unauthorized('/api/conhecimentos/0')
        self.unauthorized('/api/conhecimentos/new/0')

    def test_invalid_login_conhecimentosEmbarque(self):
        self.invalid_login('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.invalid_login('/api/conhecimentosEmbarque/0')
        self.invalid_login('/api/conhecimentosEmbarque/new/0')
        self.invalid_login('/api/conhecimentos?numeroCEmercante=0')
        self.invalid_login('/api/conhecimentos')
        self.invalid_login('/api/conhecimentos/new/0')

    def test_not_allowed_conhecimentosEmbarque(self):
        self.not_allowed('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.not_allowed('/api/conhecimentosEmbarque/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentosEmbarque/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentos?numeroCEmercante=0')
        self.not_allowed('/api/conhecimentos/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentos/new/0', methods=['POST', 'PUT', 'DELETE'])

    def test_conhecimentosEmbarque_get(self):
        self.login()
        metadata.create_all(self.sql)
        self._case('GET', '/api/conhecimentosEmbarque/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        ins = t_conhecimentosEmbarque.insert()
        create_date = '2019-01-01 00:00:00'
        rp = conn.execute(ins, **{'numeroCEmercante': '000',
                                  'last_modified': parser.parse(create_date)})
        rp = conn.execute(ins, **{'numeroCEmercante': '000'})
        r = self._case('GET', '/api/conhecimentosEmbarque/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentosEmbarque',
                       status_code=200,
                       query_dict={'numeroCEmercante': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentosEmbarque/new/%s' % create_date,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)

    def test_conhecimentos_get(self):
        self.login()
        metadata.create_all(self.sql)
        self._case('GET', '/api/conhecimentos/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        ins = conhecimentos.insert()
        last_modified = '2019-01-01 00:00:00'
        rp = conn.execute(ins, **{'numeroCEmercante': '000',
                                  'ID': 1,
                                  'last_modified': parser.parse(last_modified)})
        r = self._case('GET', '/api/conhecimentos/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentos',
                       status_code=200,
                       query_dict={'numeroCEmercante': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentos/new/%s' % last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
