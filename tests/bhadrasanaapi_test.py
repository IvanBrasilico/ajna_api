# Tescases for bhadrasanaapi
import json

from gridfs import GridFS

from bhadrasana.models.ovr import OVR, TGOVR
from bhadrasana.models.rvf import RVF, ImagemRVF
from tests.base_api_test import ApiTestCase


from bhadrasana.models import ovr

class BhadrasanaApiTestCase(ApiTestCase):

    def setUp(self):
        super().setUp()
        ovr.Base.metadata.create_all(self.sql)


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
        self.unauthorized('/api/itemtg/0')
        self.unauthorized('/api/itenstg/0')
        self.unauthorized('/api/minhas_fichas/0')
        self.unauthorized('/api/consulta_conteiner', method='POST')
        self.unauthorized('/api/consulta_empresa', method='POST')

    def test_invalid_login_ficha(self):
        self.invalid_login('/api/ficha/0')
        self.invalid_login('/api/rvf/0')
        self.invalid_login('/api/tg/0')
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

    def test_1ficha_get(self):
        self.login()
        self._case('GET', '/api/ficha/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = self.create_ovr('1')
        r = self._case('GET', '/api/ficha/%s' % ovr1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == ovr1.id
        assert r['numero'] == ovr1.numero


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
        rvf1 = self.create_rvf(1)
        r = self._case('GET', '/api/rvf/%s' % rvf1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == rvf1.id
        assert r['ovr_id'] == rvf1.ovr_id

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


