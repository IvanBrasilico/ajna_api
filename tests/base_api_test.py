# Tescases for virasana.app.py
import json
import unittest

from werkzeug.exceptions import BadRequest

from ajna_commons.flask.user import DBUser
from ajnaapi import create_app
from ajnaapi.config import Testing


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(Testing)
        self.app = app
        app.testing = True
        self.client = app.test_client()
        self.db = app.config['mongodb']
        DBUser.dbsession = self.db
        DBUser.add('ajna', 'ajna')

    def tearDown(self):
        self.db.drop_collection('users')
        self.db.drop_collection('fs.files')

    def app_test(self, method, url, query_dict, headers={}):
        print('################', query_dict)
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
        elif method == 'PUT':
            return self.client.put(
                url,
                data=json.dumps(query_dict),
                content_type='application/json',
                headers=headers
            )
        elif method == 'DELETE':
            return self.client.delete(
                url,
                data=json.dumps(query_dict),
                content_type='application/json',
                headers=headers
            )

    def _case(self, method='POST',
              url='api/login',
              query_dict=None,
              status_code=200,
              msg='',
              headers={}):
        r = self.app_test(method, url, query_dict, headers)
        print(r.status_code)
        print(r.data)
        assert r.status_code == status_code
        try:
            ljson = r.json
            if not msg:
                return ljson
            print(ljson)
            if ljson and msg:
                assert ljson.get('msg') == msg
        except json.JSONDecodeError as err:
            print(err)
            assert False
        except BadRequest as err:
            print(err)
        return r

    def login(self, username='ajna', password='ajna'):
        rv = self.client.post(
            'api/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json')
        token = rv.json.get('access_token')
        self.headers = {'Authorization': 'Bearer %s' % token}

    def unauthorized(self, url: str, method='GET'):
        self._case(method, url,
                   status_code=401,
                   msg='Missing Authorization Header')

    def invalid_login(self, url: str, method='GET'):
        self.login(username='banana')
        self._case(method, url,
                   status_code=422,
                   headers=self.headers)

    def not_allowed(self, url: str, methods=['PUT', 'DELETE']):
        for method in methods:
            self._case(method, url,
                       status_code=405, )
