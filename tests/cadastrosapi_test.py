# Tescases for cadastrosapi blueprint
import json

from bhadrasana.models.laudo import Base, Empresa, NCM
from tests.base_api_test import ApiTestCase


class CadastrosApiTestCase(ApiTestCase):

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

    def test_empresa_erros(self):
        self.not_allowed('/api/empresa/0', methods=['POST', 'PUT', 'DELETE'])
        rv = self._case('GET', '/api/empresa/0',  # minimo 8 digitos
                        status_code=400)
        assert '8' in rv['msg']
        self.not_allowed('/api/empresas/0', methods=['POST', 'PUT', 'DELETE'])
        rv = self._case('GET', '/api/empresas/0',  # minimo 8 digitos
                        status_code=400)
        assert '8' in rv['msg']

    def test_empresa(self):
        self._case('GET', '/api/empresa/00000000',
                   status_code=404)
        empresa = Empresa()
        empresa.cnpj = '00000000'
        empresa.nome = 'teste'
        self.db_session.add(empresa)
        self.db_session.commit()
        self._case('GET', '/api/empresa/00000000',
                   status_code=200)

    def test_empresas(self):
        self._case('GET', '/api/empresas/00000001',
                   status_code=404)
        empresa = Empresa()
        empresa.cnpj = '00000001'
        empresa.nome = 'teste2'
        self.db_session.add(empresa)
        self.db_session.commit()
        self._case('GET', '/api/empresas/00000001',
                   status_code=200)

    def test_ncm_erros(self):
        self.not_allowed('/api/ncm/0', methods=['POST', 'PUT', 'DELETE'])
        rv = self._case('GET', '/api/ncm/0',  # minimo 8 digitos
                        status_code=400)
        assert 'formato' in rv['msg']

    def test_ncm(self):
        self._case('GET', '/api/ncm/9503.00.21',
                   status_code=404)
        ncm = NCM()
        ncm.title = '9503.00.21'
        ncm.nome = 'teste'
        self.db_session.add(ncm)
        self.db_session.commit()
        self._case('GET', '/api/ncm/9503.00.21',
                   status_code=200)
