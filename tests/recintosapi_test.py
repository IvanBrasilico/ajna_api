# Tescases for mercanteapi blueprint
import json

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

    def test_acessoveiculo(self):
        self.invalid_login('/api/acessoveiculo/0')
        self.unauthorized('/api/acessoveiculo/0')
        self.not_allowed('/api/acessoveiculo/0', methods=['POST', 'PUT', 'DELETE'])
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
        self.db_session.add(acessoveiculo)
        self.db_session.commit()
        self.db_session.refresh(acessoveiculo)
        self._case('GET', '/api/acessoveiculo/%s' % acessoveiculo.id,
                   status_code=200,
                   headers=self.headers)

    def test_pesagemveiculo(self):
        self.invalid_login('/api/pesagemveiculo/0')
        self.unauthorized('/api/pesagemveiculo/0')
        self.not_allowed('/api/pesagemveiculo/0', methods=['POST', 'PUT', 'DELETE'])
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
        self.db_session.add(pesagemveiculo)
        self.db_session.commit()
        self.db_session.refresh(pesagemveiculo)
        self._case('GET', '/api/pesagemveiculo/%s' % pesagemveiculo.id,
                   status_code=200,
                   headers=self.headers)


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
