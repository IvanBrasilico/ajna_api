# Tescases for mercanteapi blueprint
import json

from ajnaapi.recintosapi import maschemas
from ajnaapi.recintosapi.models import Base, AcessoVeiculo, PesagemVeiculo
from tests.base_api_test import ApiTestCase


class RecintosApiTestCase(ApiTestCase):

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

    def test_acessoveiculo_erros(self):
        self.invalid_login('/api/acessoveiculo/0')
        self.unauthorized('/api/acessoveiculo/0')
        self.not_allowed('/api/acessoveiculo/0', methods=['POST', 'PUT', 'DELETE'])

    def test_acessoveiculo(self):
        self.login()
        self._case('GET', '/api/acessoveiculo/0',
                   status_code=404,
                   headers=self.headers)
        acessoveiculo = AcessoVeiculo(idEvento=1,
                                      dtHrOcorrencia='2020-01-01',
                                      cpfOperOcor='1',
                                      dtHrRegistro='2020-01-01',
                                      cpfOperReg='1',
                                      protocoloEventoRetifCanc=None,
                                      contingencia=False,
                                      recinto='T',
                                      placa='ABC')
        acessoveiculo_schema = maschemas.AcessoVeiculo()
        data = acessoveiculo_schema.dump(acessoveiculo)
        rv = self._case('POST', '/api/acessoveiculo',
                        query_dict=data,
                        status_code=201,
                        headers=self.headers)
        inserted_id = rv['id']
        rv = self._case('GET', '/api/acessoveiculo/%s' % inserted_id,
                        status_code=200,
                        headers=self.headers)
        for campo, valor in rv.items():
            if campo != 'id':
                assert data[campo] == valor
        rv = self._case(
            'GET',
            '/api/resumo_evento?tipo={}&recinto={}&id={}'.format(
                'AcessoVeiculo', 'T', inserted_id),
            status_code=200,
            headers=self.headers)
        assert b'ABC' in rv.data

    def test_pesagemveiculo_erros(self):
        self.invalid_login('/api/pesagemveiculo/0')
        self.unauthorized('/api/pesagemveiculo/0')
        self.not_allowed('/api/pesagemveiculo/0', methods=['POST', 'PUT', 'DELETE'])

    def test_pesagemveiculo(self):
        self.login()
        self._case('GET', '/api/pesagemveiculo/0',
                   status_code=404,
                   headers=self.headers)
        pesagemveiculo = PesagemVeiculo(idEvento=1,
                                        dtHrOcorrencia='2020-01-01',
                                        cpfOperOcor='1',
                                        dtHrRegistro='2020-01-01',
                                        cpfOperReg='1',
                                        protocoloEventoRetifCanc=None,
                                        contingencia=False,
                                        recinto='T',
                                        placa='ABC')
        pesagemveiculo_schema = maschemas.PesagemVeiculo()
        data = pesagemveiculo_schema.dump(pesagemveiculo)
        rv = self._case('POST', '/api/pesagemveiculo',
                        query_dict=data,
                        status_code=201,
                        headers=self.headers)
        inserted_id = rv['id']
        rv = self._case('GET', '/api/pesagemveiculo/%s' % inserted_id,
                        status_code=200,
                        headers=self.headers)
        for campo, valor in rv.items():
            if campo != 'id':
                assert data[campo] == valor
        rv = self._case(
            'GET',
            '/api/resumo_evento?tipo={}&recinto={}&id={}&format=text'.format(
                'PesagemVeiculo', 'T', inserted_id),
            status_code=200,
            headers=self.headers)
        assert b'ABC' in rv.data


if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker, scoped_session
    from ajnaapi.config import Testing

    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=Testing.sql))
    Base.query = db_session.query_property()
    Base.metadata.create_all(Testing.sql)
    acessoveiculo = AcessoVeiculo(idEvento=1,
                                  dtHrOcorrencia='2020-01-01',
                                  cpfOperOcor='1',
                                  dtHrRegistro='2020-01-01',
                                  cpfOperReg='1',
                                  protocoloEventoRetifCanc=None,
                                  contingencia=False,
                                  recinto='T',
                                  placa='ABC')
    pesagemveiculo = PesagemVeiculo(idEvento=1,
                                    dtHrOcorrencia='2020-01-01',
                                    cpfOperOcor='1',
                                    dtHrRegistro='2020-01-01',
                                    cpfOperReg='1',
                                    protocoloEventoRetifCanc=None,
                                    contingencia=False,
                                    recinto='T',
                                    placa='ABC')
    db_session.add(acessoveiculo)
    db_session.add(pesagemveiculo)
    db_session.commit()
