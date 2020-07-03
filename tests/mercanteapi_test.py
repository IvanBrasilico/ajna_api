# Tescases for mercanteapi blueprint
import json
from dateutil import parser


from tests.base_api_test import ApiTestCase

from virasana.integracao.mercante.mercantealchemy import Base, Item, NCMItem, ConteinerVazio, Escala
from virasana.integracao.mercante.mercantealchemy import Conhecimento, Manifesto




class MercanteApiTestCase(ApiTestCase):


    def setUp(self):
        super().setUp()
        Base.query = self.db_session.query_property()
        Base.metadata.drop_all(self.sql)
        Base.metadata.create_all(self.sql)

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_(self):
        self.unauthorized('/api/conhecimentos?numeroCEmercante=0')
        self.unauthorized('/api/conhecimentos/0')
        self.unauthorized('/api/conhecimentos/new/0')
        self.unauthorized('/api/manifestos?numero=0')
        self.unauthorized('/api/manifestos/0')
        self.unauthorized('/api/manifestos/new/0')
        self.unauthorized('/api/itens?numero=0')
        self.unauthorized('/api/item/0/0')
        self.unauthorized('/api/itens/new/0')
        self.unauthorized('/api/NCMItem?numero=0')
        self.unauthorized('/api/NCMItem/0/0')
        self.unauthorized('/api/NCMItem/new/0')
        self.unauthorized('/api/ConteinerVazio?manifesto=0')
        self.unauthorized('/api/ConteinerVazio/0')
        self.unauthorized('/api/ConteinerVazio/new/0')

    def test_invalid_login_(self):
        self.invalid_login('/api/conhecimentos?numeroCEmercante=0')
        self.invalid_login('/api/conhecimentos')
        self.invalid_login('/api/conhecimentos/new/0')
        self.invalid_login('/api/manifestos?numero=0')
        self.invalid_login('/api/manifestos/0')
        self.invalid_login('/api/manifestos/new/0')
        self.invalid_login('/api/itens?numero=0')
        self.invalid_login('/api/item/0/0')
        self.invalid_login('/api/itens/0')
        self.invalid_login('/api/itens/new/0')
        self.invalid_login('/api/NCMItem?numero=0')
        self.invalid_login('/api/NCMItem/0/0')
        self.invalid_login('/api/NCMItem/0')
        self.invalid_login('/api/NCMItem/new/0')
        self.invalid_login('/api/ConteinerVazio?manifesto=0')
        self.invalid_login('/api/ConteinerVazio/0')
        self.invalid_login('/api/ConteinerVazio/new/0')

    def test_not_allowed_(self):
        self.not_allowed('/api/conhecimentos?numeroCEmercante=0')
        self.not_allowed('/api/conhecimentos/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/conhecimentos/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/manifestos?numero=0')
        self.not_allowed('/api/manifestos/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/manifestos/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens?numero=0')
        self.not_allowed('/api/item/0/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/itens/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem?numero=0')
        self.not_allowed('/api/NCMItem/0/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/NCMItem/new/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/ConteinerVazio?manifesto=0')
        self.not_allowed('/api/ConteinerVazio/0', methods=['POST', 'PUT', 'DELETE'])
        self.not_allowed('/api/ConteinerVazio/new/0', methods=['POST', 'PUT', 'DELETE'])

    def test_error_conhecimentos(self):
        self.login()
        rv = self.client.get('/api/conhecimentos/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/itens/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/NCMItem/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400
        rv = self.client.get('/api/ConteinerVazio/new/datainvalida',
                             headers=self.headers)
        assert rv.status_code == 400


    def test_conhecimentos_get(self):
        self.login()
        self._case('GET', '/api/conhecimentos/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conhecimento = Conhecimento()
        conhecimento.numeroCEmercante = '000'
        conhecimento.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(conhecimento)
        self.db_session.commit()
        r = self._case('GET', '/api/conhecimentos/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentos',
                       status_code=200,
                       query_dict={'numeroCEmercante': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/conhecimentos/new/%s' % conhecimento.last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)


    def test_manifestos(self):
        self.login()
        self._case('GET', '/api/manifestos/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        manifesto = Manifesto()
        manifesto.numero = '000'
        manifesto.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(manifesto)
        self.db_session.commit()
        r = self._case('GET', '/api/manifestos/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/manifestos',
                       status_code=200,
                       query_dict={'numero': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/manifestos/new/%s' % manifesto.last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)



    def test_itens(self):
        self.login()
        self._case('GET', '/api/itens/00001',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        conhecimento = Conhecimento()
        conhecimento.numeroCEmercante = '00001'
        conhecimento.last_modified = parser.parse('2019-01-01 00:00:00')
        item = Item()
        item.numeroCEmercante = conhecimento.numeroCEmercante
        item.numeroSequencialItemCarga = '01'
        item.codigoConteiner = 'ABCD1'
        item.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(conhecimento)
        self.db_session.add(item)
        self.db_session.commit()
        r = self._case('GET', '/api/itens/00001',
                       status_code=200,
                       headers=self.headers)
        r = self._case('GET', '/api/item/00001/01',
                       status_code=200,
                       headers=self.headers)
        r = self._case('GET', '/api/itens',
                       status_code=200,
                       query_dict={'codigoConteiner': item.codigoConteiner},
                       headers=self.headers)
        r = self._case('GET', '/api/itens/new/%s' % item.last_modified,
                       status_code=200,
                       headers=self.headers)



    def test_NCMItem(self):
        self.login()
        self._case('GET', '/api/NCMItem/00001',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        conhecimento = Conhecimento()
        conhecimento.numeroCEmercante = '00001'
        conhecimento.last_modified = parser.parse('2019-01-01 00:00:00')
        item = NCMItem()
        item.numeroCEMercante = conhecimento.numeroCEmercante
        item.numeroSequencialItemCarga = '01'
        item.identificacaoNCM = 'ABCD1'
        item.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(conhecimento)
        self.db_session.add(item)
        self.db_session.commit()
        r = self._case('GET', '/api/NCMItem/00001',
                       status_code=200,
                       headers=self.headers)
        r = self._case('GET', '/api/NCMItem/00001/01',
                       status_code=200,
                       headers=self.headers)
        r = self._case('GET', '/api/NCMItem',
                       status_code=200,
                       query_dict={'identificacaoNCM': item.identificacaoNCM},
                       headers=self.headers)
        r = self._case('GET', '/api/NCMItem/new/%s' % item.last_modified,
                       status_code=200,
                       headers=self.headers)



    def test_ConteinerVazio(self):
        self.login()
        self._case('GET', '/api/ConteinerVazio/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        conn = self.sql.connect()
        manifesto = Manifesto()
        manifesto.numero = '000'
        manifesto.last_modified = parser.parse('2019-01-01 00:00:00')
        conteiner = ConteinerVazio()
        conteiner.manifesto = manifesto.numero
        conteiner.idConteinerVazio = 'ABCD123'
        conteiner.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(manifesto)
        self.db_session.add(conteiner)
        self.db_session.commit()
        r = self._case('GET', '/api/ConteinerVazio/%s' % manifesto.numero,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/ConteinerVazio',
                       status_code=200,
                       query_dict={'idConteinerVazio': conteiner.idConteinerVazio},
                       headers=self.headers)
        r = self._case('GET', '/api/ConteinerVazio/new/%s' % conteiner.last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)


    def test_escalas_get(self):
        self.login()
        self._case('GET', '/api/escalas/000',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        escala = Escala()
        escala.numeroDaEscala = '000'
        escala.last_modified = parser.parse('2019-01-01 00:00:00')
        self.db_session.add(escala)
        self.db_session.commit()
        r = self._case('GET', '/api/escalas/000',
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
        r = self._case('GET', '/api/escalas',
                       status_code=200,
                       query_dict={'numeroDaEscala': '000'},
                       headers=self.headers)
        r = self._case('GET', '/api/escalas/new/%s' % escala.last_modified,
                       status_code=200,
                       query_dict={},
                       headers=self.headers)
