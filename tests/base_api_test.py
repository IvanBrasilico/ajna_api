# Tescases for virasana.app.py
import json
import unittest

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
        # self.db.drop_collection('users')
        pass

    def app_test(self, method, url, pjson):
        if method == 'POST':
            return self.client.post(
                url,
                data=json.dumps(pjson),
                content_type='application/json')
        else:
            return self.client.get(url)

    def _case(self, method='POST',
              url='api/login',
              pjson=None,
              status_code=200,
              msg=''):
        try:
            r = self.app_test(method, url, pjson)
            print(r.status_code)
            print(r.data)
            print(r.json)
            assert r.status_code == status_code
            if r.json and msg:
                assert r.json.get('msg') == msg
        except json.JSONDecodeError as err:
            print(err)
            assert False

