from .config import Config
from flask import Flask
from ajna_commons.flask import api_login

from app.endpoints import api


def create_app(config_class=Config):
    app = Flask(__name__)
    #app.config['SERVER_NAME'] = 'ajna.api'
    app.secret_key = config_class.SECRET
    app.config['mongodb'] = config_class.db
    api_login.configure(app)
    app.register_blueprint(api)
    return app

