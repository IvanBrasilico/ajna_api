# Tescases for mercanteapi blueprint
import json
from sqlalchemy import create_engine
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
        rp = conn.execute(ins, **{'numeroCEmercante': '000'})
        print(rp, rp.rowcount)
        sel = t_conhecimentosEmbarque.select(
            ).where(t_conhecimentosEmbarque.c.numeroCEmercante == '000')
        rp = conn.execute(sel)
        rp.fetchall()
        for row in rp:
            print(row)
            print(row[0])
            print(row['numeroCEmercante'])
        print(rp, rp.rowcount)

        r = self._case('GET', '/api/conhecimentosEmbarque/000',
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
        rp = conn.execute(ins, **{'numeroCEmercante': '000', 'ID': 1})
        r = self._case('GET', '/api/conhecimentos/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
