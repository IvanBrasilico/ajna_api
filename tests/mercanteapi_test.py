# Tescases for mercanteapi blueprint
import json
from dateutil import parser
from integracao.mercantealchemy import metadata
from integracao.mercantealchemy import (conhecimentos, conteineresVazios, itens,
                                        manifestos, NCMItem, t_conhecimentosEmbarque)

from tests.base_api_test import ApiTestCase


class MercanteApiTestCase(ApiTestCase):

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_(self):
        self.unauthorized('/api/conhecimentosEmbarque')
        self.unauthorized('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.unauthorized('/api/conhecimentosEmbarque/0')
        self.unauthorized('/api/conhecimentosEmbarque/new/0')
        self.unauthorized('/api/conhecimentos?numeroCEmercante=0')
        self.unauthorized('/api/conhecimentos/0')
        self.unauthorized('/api/conhecimentos/new/0')
        self.unauthorized('/api/manifestos?numero=0')
        self.unauthorized('/api/manifestos/0')
        self.unauthorized('/api/manifestos/new/0')
        self.unauthorized('/api/itens?numero=0')
        self.unauthorized('/api/itens/0/0')
        self.unauthorized('/api/itens/new/0')
        self.unauthorized('/api/NCMItem?numero=0')
        self.unauthorized('/api/NCMItem/0/0')
        self.unauthorized('/api/NCMItem/new/0')
        self.unauthorized('/api/conteineresVazios?manifesto=0')
        self.unauthorized('/api/conteineresVazios/0')
        self.unauthorized('/api/conteineresVazios/new/0')

    def test_invalid_login_(self):
        self.invalid_login('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.invalid_login('/api/conhecimentosEmbarque/0')
        self.invalid_login('/api/conhecimentosEmbarque/new/0')
        self.invalid_login('/api/conhecimentos?numeroCEmercante=0')
        self.invalid_login('/api/conhecimentos')
        self.invalid_login('/api/conhecimentos/new/0')
        self.invalid_login('/api/manifestos?numero=0')
        self.invalid_login('/api/manifestos/0')
        self.invalid_login('/api/manifestos/new/0')
        self.invalid_login('/api/itens?numero=0')
        self.invalid_login('/api/itens/0/0')
        self.invalid_login('/api/itens/0')
        self.invalid_login('/api/itens/new/0')
        self.invalid_login('/api/NCMItem?numero=0')
        self.invalid_login('/api/NCMItem/0/0')
        self.invalid_login('/api/NCMItem/0')
        self.invalid_login('/api/NCMItem/new/0')
        self.invalid_login('/api/conteineresVazios?manifesto=0')
        self.invalid_login('/api/conteineresVazios/0')
        self.invalid_login('/api/conteineresVazios/new/0')

    def test_not_allowed_(self):
        self.not_allowed('/api/conhecimentosEmbarque?numeroCEmercante=0')
        self.not_allowed('/api/conhecimentosEmbarque/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentosEmbarque/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentos?numeroCEmercante=0')
        self.not_allowed('/api/conhecimentos/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentos/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/manifestos?numero=0')
        self.not_allowed('/api/manifestos/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/manifestos/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens?numero=0')
        self.not_allowed('/api/itens/0/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem?numero=0')
        self.not_allowed('/api/NCMItem/0/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conteineresVazios?manifesto=0')
        self.not_allowed('/api/conteineresVazios/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conteineresVazios/new/0', methods=['POST', 'PUT', 'DELETE'])

    def test_error_conhecimentos(self):
        self.login()
        rv = self.client.get('/api/conhecimentosEmbarque?camponaoexiste=nao',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/conhecimentos?camponaoexiste=nao',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/conhecimentosEmbarque/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/conhecimentos/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/itens/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/NCMItem/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/conteineresVazios/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400

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


    def test_manifestos(self):
        self.login()
        metadata.create_all(self.sql)
        self._case('GET', '/api/manifestos/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        ins = manifestos.insert()
        last_modified = '2019-01-01 00:00:00'
        rp = conn.execute(ins, **{'numero': '000',
                                  'ID': 1,
                                  'last_modified': parser.parse(last_modified)})
        r = self._case('GET', '/api/manifestos/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/manifestos',
                       status_code=200,
                       query_dict={'numero': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/manifestos/new/%s' % last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
