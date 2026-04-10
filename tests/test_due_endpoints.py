import json
import unittest
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from ajna_commons.flask.user import DBUser, DBType
from ajnaapi.main import create_app
from ajnaapi.config import Testing
from bhadrasana.models import Usuario
from bhadrasana.models import Base as UBase
from virasana.integracao.due.due_alchemy import Base, Due, DueItem  # Ajuste o import conforme seu módulo


class DueApiTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(Testing)
        self.app = app
        app.testing = True
        self.client = app.test_client()
        self.db = app.config['mongodb']
        self.sql = app.config['sql']
        self.engine = self.sql
        self.db_session = app.config['db_session']
        DBUser.dbsession = self.db_session
        DBUser.alchemy_class = Usuario

        # Criar tabelas
        Base.metadata.create_all(self.sql, [
            Base.metadata.tables['pucomex_due'],
            Base.metadata.tables['pucomex_due_itens'],
        ])
        UBase.metadata.create_all(self.sql, [
            UBase.metadata.tables['ovr_usuarios']
        ])

        DBUser.add('ajna', 'ajna')
        self.login()

    def tearDown(self):
        self.db.drop_collection('fs.files')
        # Limpar dados de teste
        self.db_session.query(Due).delete()
        self.db_session.query(DueItem).delete()
        self.db_session.commit()

    def _due_payload(self, numero_due='12345678901234'):
        """Payload padrão para criar DUE"""
        return {
            'numero_due': numero_due,
            'ni_declarante': '11111111111111',
            'cnpj_estabelecimento_exportador': '22222222222222',
            'telefone_contato': '11999998888',
            'email_contato': 'contato@exemplo.com',
            'nome_contato': 'João Silva',
            'codigo_iso3_pais_importador': 'ARG',
            'nome_pais_importador': 'Argentina',
            'duev_nm_tp_doc_fiscal_c': 'NF-e',
            'duev_cetp_nm_c': 'CNPJ',
            'codigo_recinto_despacho': '1234567',
            'codigo_recinto_embarque': '7654321',
            'codigo_unidade_embarque': '9876543',
            'lista_id_conteiner': 'CONT001, CONT002'
        }

    def _due_item_payload(self, due_nr_item=1, nr_due='12345678901234'):
        """Payload padrão para criar DueItem"""
        return {
            'nr_due': nr_due,
            'due_nr_item': due_nr_item,
            'descricao_item': 'CARNE BOVINA',
            'descricao_complementar_item': 'CORTE CONGELADO',
            'nfe_nr_item': 10,
            'nfe_ncm': '02023000',
            'unidade_comercial': 'KG',
            'qt_unidade_comercial': 1500.75,
            'valor_total_due_itens': 25400.90,
            'nfe_nm_importador': 'IMPORTADOR XYZ',
            'pais_destino_item': 'Chile'
        }

    def app_test(self, method, url, query_dict, headers=None):
        print('################', query_dict)
        headers = headers or {}
        headers.update(self.headers)

        if method == 'POST':
            return self.client.post(
                url,
                data=json.dumps(query_dict),
                content_type='application/json',
                headers=headers
            )
        elif method == 'GET':
            return self.client.get(
                url,
                query_string=query_dict,
                headers=headers
            )

        raise ValueError(f'Método HTTP não suportado no teste: {method}')

    def _case(self, method='POST',
              url='/api/dues',
              query_dict=None,
              status_code=200,
              msg='',
              headers={}):
        r = self.app_test(method, url, query_dict or {}, headers)
        print(r.status_code)
        print(r.data)
        assert r.status_code == status_code
        try:
            ljson = r.json
            if ljson:
                if not msg:
                    return ljson
                print(ljson)
                if ljson and msg:
                    assert ljson.get('msg') == msg
        except json.JSONDecodeError as err:
            print(err)
            assert False
        return r

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            '/api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': f'Bearer {token}'}

    # Testes para /api/dues (GET)
    def test_dues_get_sem_filtro(self):
        due_data = self._due_payload()
        self._case('POST', query_dict=due_data, status_code=201)
        self._case('GET', status_code=200)

    def test_dues_get_com_filtro(self):
        # Primeiro criar uma DUE para testar filtro
        due_data = self._due_payload()
        self._case('POST', query_dict=due_data, status_code=201)

        filtro = {'ni_declarante': due_data['ni_declarante']}
        result = self._case('GET', query_dict=filtro, status_code=200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['numero_due'], due_data['numero_due'])

    # Testes para /api/dues (POST)
    def test_dues_post_criacao(self):
        payload = self._due_payload()
        result = self._case('POST', query_dict=payload, status_code=201)
        self.assertEqual(result['msg'], 'DUE criada com sucesso')
        self.assertEqual(result['numero_due'], payload['numero_due'])

    def test_dues_post_update(self):
        payload = self._due_payload()
        self._case('POST', query_dict=payload, status_code=201)

        # Atualizar com novos dados
        payload['telefone_contato'] = '11999998888'
        result = self._case('POST', query_dict=payload, status_code=201)
        self.assertEqual(result['msg'], 'DUE atualizada com sucesso')

    def test_dues_post_sem_numero_due(self):
        payload = self._due_payload()
        del payload['numero_due']
        self._case('POST', query_dict=payload, status_code=400, msg='numero_due é obrigatório')

    # Testes para /api/dues/bulk
    def test_dues_bulk_sucesso_total(self):
        payload = {
            'items': [
                self._due_payload(numero_due='12345678901234'),
                self._due_payload(numero_due='98765432109876')
            ]
        }
        result = self._case(
            method='POST',
            url='/api/dues/bulk',
            query_dict=payload,
            status_code=201
        )
        self.assertEqual(result['summary']['total'], 2)
        self.assertEqual(result['summary']['created'], 2)
        self.assertEqual(result['summary']['failed'], 0)

