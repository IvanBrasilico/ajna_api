# Tescases for bhadrasanaapi
import json

from gridfs import GridFS

from bhadrasana.models.ovr import OVR
from bhadrasana.models.rvf import RVF
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

    """
    def test_unauthorized_ficha(self):
        self.unauthorized('/api/ficha/0')
        self.unauthorized('/api/rvf/0')

    def test_invalid_login_ficha(self):
        self.invalid_login('/api/ficha/0')
        self.invalid_login('/api/rvf/0')

    def test_not_allowed_ficha(self):
        self.not_allowed('/api/ficha/0')
        self.not_allowed('/api/rvf/0')
    """
    def test_1ficha_get(self):
        self.login()
        self._case('GET', '/api/ficha/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        ovr1 = OVR()
        ovr1.numero = '1'
        self.db_session.add(ovr1)
        self.db_session.commit()
        self.db_session.refresh(ovr1)
        r = self._case('GET', '/api/ficha/%s' % ovr1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == ovr1.id
        assert r['numero'] == ovr1.numero


    def test_2rvf_get(self):
        self.login()
        self._case('GET', '/api/rvf/0',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        rvf1 = RVF()
        rvf1.ovr_id = 1
        self.db_session.add(rvf1)
        self.db_session.commit()
        self.db_session.refresh(rvf1)
        r = self._case('GET', '/api/rvf/%s' % rvf1.id,
                       status_code=200,
                       headers=self.headers)
        assert r['id'] == rvf1.id
        assert r['ovr_id'] == rvf1.ovr_id
