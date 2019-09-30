# Tescases for virasana.app.py
import unittest

from flask import Flask, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient

import ajna_commons.flask.login as login
from ajna_commons.flask.user import DBUser
from app.config import Testing
from app import create_app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(Testing)
        app.testing = True
        self.client = app.test_client()
        self.db = app.config['mongodb']
        DBUser.dbsession = self.db
        DBUser.add('ajna', 'ajna')

    def tearDown(self):
        self.db.drop_collection('users')
        rv = self.logout()
        assert rv is not None

    def get_token(self, url):
        response = self.client.get(url, follow_redirects=True)
        csrf_token = response.data.decode()
        begin = csrf_token.find('csrf_token"') + 10
        end = csrf_token.find('username"') - 10
        csrf_token = csrf_token[begin: end]
        begin = csrf_token.find('value="') + 7
        end = csrf_token.find('/>')
        self.csrf_token = csrf_token[begin: end]
        return self.csrf_token

    def login(self, username, senha):
        self.get_token('/login')
        return self.client.post('/login', data=dict(
            username=username,
            senha=senha,
            csrf_token=self.csrf_token
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logoout', follow_redirects=True)

    def test_login_invalido(self):
        rv = self.login('none', 'error')
        print(rv.data)
        assert rv is not None
        assert b'username' in rv.data

    def test_login(self):
        rv = self.login('ajna', 'ajna')
        assert rv is not None
        assert b'autenticado' in rv.data

    def test_DBuser(self):
        auser = DBUser.get('ajna')
        assert auser.name == 'ajna'
        auser2 = DBUser.get('ajna', 'ajna')
        assert auser2.name == 'ajna'
        # Testa mundança de senha
        DBUser.add('ajna', '1234')
        auser3 = DBUser.get('ajna', 'ajna')
        assert auser3 is None
        auser4 = DBUser.get('ajna', '1234')
        assert auser4.name == 'ajna'

    def test_404(self):
        rv = self.client.get('/non_ecsiste')
        assert rv is not None
        assert b'404' in rv.data
