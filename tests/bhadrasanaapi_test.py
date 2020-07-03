# Tescases for bhadrasanaapi
import json
from datetime import datetime

from tests.base_api_test import ApiTestCase

import virasana.integracao.mercante.mercantealchemy as mercante
from ajnaapi.recintosapi import models as recintosapi_models
from bhadrasana.models import ovr, Usuario
from bhadrasana.models.ovr import OVR, TGOVR, ItemTG
from bhadrasana.models.rvf import RVF, ImagemRVF
from bhadrasana.models import laudo


class BhadrasanaApiTestCase(ApiTestCase):

    def setUp(self):
        super().setUp()
        ovr.Base.metadata.create_all(self.sql)
        mercante.metadata.create_all(self.sql, [
            mercante.metadata.tables['itensresumo'],
            mercante.metadata.tables['ncmitemresumo'],
            mercante.metadata.tables['conhecimentosresumo']
        ])
        recintosapi_models.Base.metadata.create_all(self.sql)
        laudo.Base.metadata.create_all(self.sql)

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_ficha(self):
        self.unauthorized('/api/ficha/0')
        self.unauthorized('/api/rvf/0')
        self.unauthorized('/api/tg/0')
        self.unauthorized('/api/fichas', method='POST')
        self.unauthorized('/api/rvfs', method='POST')
        self.unauthorized('/api/tgs', method='POST')
        self.unauthorized('/api/itemtg/0')
        self.unauthorized('/api/itenstg/0')
        self.unauthorized('/api/minhas_fichas/0')
        self.unauthorized('/api/consulta_conteiner', method='POST')
        self.unauthorized('/api/consulta_empresa', method='POST')

    def test_invalid_login_ficha(self):
        self.invalid_login('/api/ficha/0')
        self.invalid_login('/api/rvf/0')
        self.invalid_login('/api/tg/0')
        self.invalid_login('/api/fichas', method='POST')
        self.invalid_login('/api/rvfs', method='POST')
        self.invalid_login('/api/tgs', method='POST')
        self.invalid_login('/api/itemtg/0')
        self.invalid_login('/api/itenstg/0')
        self.invalid_login('/api/minhas_fichas/0')
        self.invalid_login('/api/consulta_conteiner', method='POST')
        self.invalid_login('/api/consulta_empresa', method='POST')

    def test_not_allowed_ficha(self):
        self.not_allowed('/api/ficha/0')
        self.not_allowed('/api/rvf/0')
        self.not_allowed('/api/tg/0')
        self.not_allowed('/api/itemtg/0')
        self.not_allowed('/api/itenstg/0')
        self.not_allowed('/api/minhas_fichas/0')
        self.not_allowed('/api/consulta_conteiner', methods=['PUT', 'DELETE', 'GET'])
        self.not_allowed('/api/consulta_empresa', methods=['PUT', 'DELETE', 'GET'])

    def create_ovr(self, numero):
        ovr = OVR()
        ovr.numero = numero
        self.db_session.add(ovr)
        self.db_session.commit()
        self.db_session.refresh(ovr)
        return ovr

    def test_1ficha(self):
        self.login()
        self._case('GET', '/api/ficha/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        self._case('POST', '/api/fichas',
                   status_code=404,
                   query_dict={'numero': '1'},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        r = self._case('GET', '/api/ficha/%s' % ovr1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == ovr1.id
        assert r['numero'] == ovr1.numero
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'id': str(ovr1.id)},
                   headers=self.headers)
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'numero': ovr1.numero},
                   headers=self.headers)
        ovr1.numeroCEmercante = '123'
        ovr1.user_name = 'ivan'
        ovr1.recinto_id = '2'
        ovr1.cnpj_fiscalizado = '456'
        self.db_session.add(ovr1)
        self.db_session.commit()
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'user_name': ovr1.user_name},
                   headers=self.headers)
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'numeroCEmercante': ovr1.numeroCEmercante},
                   headers=self.headers)
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'recinto_id': ovr1.recinto_id},
                   headers=self.headers)
        self._case('POST', '/api/fichas',
                   status_code=200,
                   query_dict={'cnpj_fiscalizado': ovr1.cnpj_fiscalizado},
                   headers=self.headers)

    def create_rvf(self, ovr_id):
        rvf = RVF()
        rvf.ovr_id = ovr_id
        self.db_session.add(rvf)
        self.db_session.commit()
        self.db_session.refresh(rvf)
        return rvf

    def test_2rvf_get(self):
        self.login()
        self._case('GET', '/api/rvf/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        self._case('POST', '/api/rvfs',
                   status_code=404,
                   query_dict={'id': 0},
                   headers=self.headers)
        rvf1 = self.create_rvf(1)
        r = self._case('GET', '/api/rvf/%s' % rvf1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == rvf1.id
        assert r['ovr_id'] == rvf1.ovr_id
        self._case('POST', '/api/rvfs',
                   status_code=200,
                   query_dict={'ovr_id': rvf1.ovr_id},
                   headers=self.headers)

    def test_3rvf_ovr_get(self):
        self.login()
        self._case('GET', '/api/rvf/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        rvf1 = self.create_rvf(ovr1.id)
        r = self._case('GET', '/api/rvfs/%s' % ovr1.id,
                       status_code=200,
                       headers=self.headers)
        assert len(r) == 1
        assert r[0]['id'] == rvf1.id
        assert r[0]['ovr_id'] == rvf1.ovr_id

    def test_4imagensrvf_get(self):
        self.login()
        self._case('GET', '/api/rvf/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        rvf1 = self.create_rvf(ovr1.id)
        imagem_rvf1 = ImagemRVF()
        imagem_rvf1.rvf_id = rvf1.id
        imagem_rvf1.marca_id = 1
        imagem_rvf2 = ImagemRVF()
        imagem_rvf2.rvf_id = rvf1.id
        self.db_session.add(imagem_rvf1)
        self.db_session.add(imagem_rvf2)
        self.db_session.commit()
        r = self._case('GET', '/api/imagens_rvf/%s' % rvf1.id,
                       status_code=200,
                       headers=self.headers)
        assert len(r) == 2
        assert r[0]['id'] == imagem_rvf1.id
        assert r[0]['rvf_id'] == imagem_rvf1.rvf_id
        assert r[0]['marca_id'] == imagem_rvf1.marca_id
        assert r[1]['id'] == imagem_rvf2.id
        assert r[1]['rvf_id'] == imagem_rvf2.rvf_id
        assert r[1]['marca_id'] is None

    def test_5tg_get(self):
        self.login()
        self._case('GET', '/api/tg/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        self._case('POST', '/api/tgs',
                   status_code=404,
                   query_dict={'id': 0},
                   headers=self.headers)
        tg = TGOVR()
        tg.numerolote = 'abcd'
        tg.descricao = 'teste'
        self.db_session.add(tg)
        self.db_session.commit()
        self.db_session.refresh(tg)
        r = self._case('GET', '/api/tg/%s' % tg.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == tg.id
        assert r['descricao'] == tg.descricao
        self._case('POST', '/api/tgs',
                   status_code=200,
                   query_dict={'id': tg.id},
                   headers=self.headers)
        self._case('POST', '/api/tgs',
                   status_code=200,
                   query_dict={'numerolote': tg.numerolote},
                   headers=self.headers)
        self._case('POST', '/api/tgs',
                   status_code=200,
                   query_dict={'descricao': tg.descricao},
                   headers=self.headers)

    def test_6tg_ovr_get(self):
        self.login()
        self._case('GET', '/api/tgs/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        tg = TGOVR()
        tg.ovr_id = ovr1.id
        tg.numerolote = 'abcd'
        tg.descricao = 'teste'
        self.db_session.add(tg)
        self.db_session.commit()
        self.db_session.refresh(tg)
        r = self._case('GET', '/api/tgs/%s' % ovr1.id,
                       status_code=200,
                       headers=self.headers)
        assert len(r) == 1
        assert r[0]['id'] == tg.id
        assert r[0]['ovr_id'] == tg.ovr_id

    def test_7itemtg_get(self):
        self.login()
        self._case('GET', '/api/itemtg/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        self._case('POST', '/api/itenstg',
                   status_code=404,
                   query_dict={'id': 0},
                   headers=self.headers)
        tg = TGOVR()
        tg.ovr_id = 1
        tg.numerolote = 'abcde'
        tg.descricao = 'teste'
        self.db_session.add(tg)
        self.db_session.commit()
        self.db_session.refresh(tg)
        itemtg = ItemTG()
        itemtg.numero = 1
        itemtg.tg_id = tg.id
        itemtg.descricao = 'teste'
        self.db_session.add(itemtg)
        self.db_session.commit()
        self.db_session.refresh(itemtg)
        r = self._case('GET', '/api/itemtg/%s' % itemtg.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == itemtg.id
        assert r['descricao'] == itemtg.descricao
        self._case('POST', '/api/itenstg',
                   status_code=200,
                   query_dict={'id': itemtg.id},
                   headers=self.headers)
        self._case('POST', '/api/itenstg',
                   status_code=200,
                   query_dict={'numero': itemtg.numero},
                   headers=self.headers)
        self._case('POST', '/api/itenstg',
                   status_code=200,
                   query_dict={'descricao': itemtg.descricao},
                   headers=self.headers)

    def test_8itemtg_tg_ovr_get(self):
        self.login()
        self._case('GET', '/api/itenstg/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        tg = TGOVR()
        tg.ovr_id = 1
        tg.numerolote = 'abcde'
        tg.descricao = 'teste'
        self.db_session.add(tg)
        self.db_session.commit()
        self.db_session.refresh(tg)
        itemtg = ItemTG()
        itemtg.numero = 1
        itemtg.tg_id = tg.id
        itemtg.descricao = 'teste'
        self.db_session.add(itemtg)
        self.db_session.commit()
        self.db_session.refresh(itemtg)
        r = self._case('GET', '/api/itenstg/%s' % tg.id,
                       status_code=200,
                       headers=self.headers)
        assert len(r) == 1
        assert r[0]['id'] == itemtg.id
        assert r[0]['tg_id'] == tg.id

    def test_cpf_telegram(self):
        self.login()
        self._case('GET', '/api/get_cpf_telegram/ivan',
                   status_code=404,
                   headers=self.headers)
        usuario = Usuario()
        usuario.telegram = 'ivan'
        usuario.cpf = 'achou'
        self.db_session.add(usuario)
        self.db_session.commit()
        r = self._case('GET', '/api/get_cpf_telegram/ivan',
                       status_code=200,
                       headers=self.headers)
        assert r['cpf'] == usuario.cpf

    def test_minhas_fichas(self):
        self.unauthorized('/api/minhas_fichas/ghost')
        self.login()
        self._case('GET', '/api/minhas_fichas/ghost',
                   status_code=404,
                   headers=self.headers)
        usuario = Usuario()
        usuario.cpf = 'ficha_test'
        ovr = OVR()
        ovr.responsavel_cpf = usuario.cpf
        self.db_session.add(usuario)
        self.db_session.add(ovr)
        self.db_session.commit()
        self._case('GET', '/api/minhas_fichas/ficha_test',
                   status_code=400,
                   headers=self.headers)
        ovr.datahora = datetime.today()
        self.db_session.add(ovr)
        self.db_session.commit()
        self._case('GET', '/api/minhas_fichas/ficha_test',
                   status_code=200,
                   headers=self.headers)

    def test_consulta_conteiner_erros(self):
        self.unauthorized('/api/consulta_conteiner', method='POST')
        self.login()
        self._case('POST', '/api/consulta_conteiner',
                   status_code=400,
                   headers=self.headers)
        query = {
            'numerolote': 'string',
            'datainicio': 'string',
            'datafim': 'string'
        }
        self._case('POST', '/api/consulta_conteiner',
                   status_code=400,
                   query_dict=query,
                   headers=self.headers)

    def test_consulta_conteiner_sucesso(self):
        self.login()
        query = {
            'numerolote': 'A',
            'datainicio': '2000-01-01',
            'datafim': '2200-12-31'
        }
        self._case('POST', '/api/consulta_conteiner',
                   status_code=200,
                   query_dict=query,
                   headers=self.headers)

    def test_consulta_empresa_erros(self):
        self.unauthorized('/api/consulta_empresa', method='POST')
        self.login()
        self._case('POST', '/api/consulta_empresa',
                   status_code=400,
                   headers=self.headers)
        query = {
            'cnpj': 'string',
            'datainicio': 'string',
            'datafim': 'string'
        }
        self._case('POST', '/api/consulta_empresa',
                   status_code=400,
                   query_dict=query,
                   headers=self.headers)

        query = {
            'cnpj': '000',  # curto
            'datainicio': '2000-01-01',
            'datafim': '2200-12-31'
        }
        self._case('POST', '/api/consulta_empresa',
                   status_code=400,
                   query_dict=query,
                   headers=self.headers)

    def test_consulta_empresa_sucesso(self):
        self.login()
        query = {
            'cnpj': '00000000',  # 8 posições
            'datainicio': '2000-01-01',
            'datafim': '2200-12-31'
        }
        self._case('POST', '/api/consulta_empresa',
                   status_code=200,
                   query_dict=query,
                   headers=self.headers)
