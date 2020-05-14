# Tescases for integracao/carga_mongo.py
import json
import unittest

from sqlalchemy.orm import scoped_session, sessionmaker

from ajnaapi.config import Staging
from ajnaapi.recintosapi import models as orm
from ajnaapi.recintosapi.usecases import UseCases
from ajnaapi.recintosapi import maschemas

RECINTO = '1'


class CargaLoaderTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = Staging.sql
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=self.engine))
        orm.Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        # self.session.remove()
        pass

    def test_load_acessoveiculo_from_json(self):
        with open('tests/json/AcessoVeiculo.json', 'r') as exemplo_in:
            acesso_json = json.load(exemplo_in)
        acesso_json['recinto'] = RECINTO
        acesso = orm.AcessoVeiculo(**acesso_json)
        print(acesso.dump())
        # assert False

    def test_insert_acessoveiculo_from_json_usecase(self):
        with open('tests/json/AcessoVeiculo.json', 'r') as exemplo_in:
            acesso_json = json.load(exemplo_in)
        usecases = UseCases(self.db_session, RECINTO)
        acesso = usecases.insert_acessoveiculo(acesso_json)
        print('11111111', acesso.dump())
        print('11111bbbb', maschemas.AcessoVeiculo().dump(acesso))
        acesso_json = usecases.load_acessoveiculo(acesso.idEvento)
        print('2222', acesso_json)
        assert False
