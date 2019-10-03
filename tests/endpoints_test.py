# Tescases for virasana.app.py
# Tescases for virasana.app.py
import json

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
                   pjson={},
                   headers=self.headers)
        _id1 = self.db.fs.files.insert_one({'teste': '1',
                                            'metadata' : {'contentType': 'text/text'}}).inserted_id
        _id2 = self.db.fs.files.insert_one({'teste': '2',
                                            'metadata': {'contentType': 'text/xml'}}).inserted_id
        self._case('GET', '/api/grid_data',
                   status_code=200,
                   pjson={'_id': str(_id1)},
                   headers=self.headers)
        # self._case('POST', '/api/grid_data',
        #           status_code=200,
        #           pjson={'query': {'_id': str(_id1)}},
        #           headers=self.headers)

    def test_unauthorized_image(self):
        self.unauthorized('/api/image/0')

    def test_invalid_login_image(self):
        self.invalid_login('/api/image/0')

    def test_not_allowed_image(self):
        self.not_allowed('/api/image/0',
                         methods=['PUT', 'DELETE', 'POST'])

    def test_unauthorized_due(self):
        self.unauthorized('/api/dues/update', 'POST')

    def test_invalid_login_due(self):
        self.invalid_login('/api/dues/update', 'POST')

    def test_not_allowed_due(self):
        self.not_allowed('/api/dues/update',
                         methods=['PUT', 'DELETE', 'GET'])


