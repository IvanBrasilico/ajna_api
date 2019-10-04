# Tescases for virasana.app.py
# Tescases for virasana.app.py
import json

from gridfs import GridFS

from tests.base_api_test import ApiTestCase


class ApiLoginTestCase(ApiTestCase):

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def test_unauthorized_grid_data(self):
        self.unauthorized('/api/grid_data')

    def test_invalid_login_grid_data(self):
        self.invalid_login('/api/grid_data')

    def test_not_allowed_data(self):
        self.not_allowed('/api/grid_data')

    def test_grid_data_get(self):
        self.login()
        self._case('GET', '/api/grid_data',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        _id1 = self.db.fs.files.insert_one({'teste': '1',
                                            'metadata': {'contentType': 'text/text'}}).inserted_id
        _id2 = self.db.fs.files.insert_one({'teste': '2',
                                            'metadata': {'contentType': 'text/xml'}}).inserted_id
        r = self._case('GET', '/api/grid_data',
                       status_code=200,
                       query_dict={'teste': '1'},
                       headers=self.headers)
        assert len(r) == 1
        assert r[0]['_id'] == str(_id1)
        r = self._case('POST', '/api/grid_data',
                       status_code=200,
                       query_dict={'query': {'teste': '2'}},
                       headers=self.headers)
        assert len(r) == 1
        assert r[0]['_id'] == str(_id2)

    def test_unauthorized_image(self):
        self.unauthorized('/api/image/0')

    def test_invalid_login_image(self):
        self.invalid_login('/api/image/0')

    def test_not_allowed_image(self):
        self.not_allowed('/api/image/0',
                         methods=['PUT', 'DELETE', 'POST'])

    def test_image(self):
        self.login()
        self._case('GET', '/api/image/0',
                   status_code=400,
                   query_dict={},
                   headers=self.headers)
        self._case('GET', '/api/image/5c5309281004b3779c37d3a2',
                   status_code=404,
                   query_dict={},
                   headers=self.headers)
        fs = GridFS(self.db)
        _id = fs.put(b'Teste', filename='teste.txt')
        print('/api/image/%s' % _id)
        r = self._case('GET', '/api/image/%s' % _id,
                       status_code=200,
                       headers=self.headers)

    def test_unauthorized_due(self):
        self.unauthorized('/api/dues/update', 'POST')

    def test_invalid_login_due(self):
        self.invalid_login('/api/dues/update', 'POST')

    def test_not_allowed_due(self):
        self.not_allowed('/api/dues/update',
                         methods=['PUT', 'DELETE', 'GET'])

    def test_due(self):
        self.login()
        fs = GridFS(self.db)
        _id = fs.put(b'Teste', filename='teste.txt')
        r = self._case('POST', '/api/dues/update',
                       status_code=201,
                       query_dict={str(_id): []},
                       headers=self.headers)

    def test_unauthorized_summary_aniita(self):
        self.unauthorized('/api/summary_aniita/0', 'GET')

    def test_invalid_login_summary_aniita(self):
        self.invalid_login('/api/summary_aniita/0', 'GET')

    def test_not_allowed_summary_aniita(self):
        self.not_allowed('/api/summary_aniita/0',
                         methods=['PUT', 'DELETE', 'POST'])

    def test_summary_aniita(self):
        self.login()
        self.db.fs.files.insert_one(
            {'metadata':
                 {'carga':
                      {
                        'conhecimento':
                           {'conhecimento': '1',
                            'consignatario': 'A'
                            },
                        'manifesto':
                            {'manifesto': 1
                            },
                        'ncm': []
                      }
                  }
             }
        )
        r = self._case('GET', '/api/summary_aniita/1',
                       status_code=200,
                       headers=self.headers)

    def test_campos_summary_aniita(self):
        self.login()
        with open('tests/exemplo_carga.json', 'r') as exemplo_in:
            exemplo = json.load(exemplo_in)
        self.db.fs.files.insert_one(exemplo)
        r = self._case('GET', '/api/summary_aniita/2',
                       status_code=200,
                       headers=self.headers)
        print(r)
        assert r.get('NIC CE Mercante') == \
               exemplo.get('metadata').get('carga').get('conhecimento').get('conhecimento')
