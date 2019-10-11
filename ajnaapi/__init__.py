from flask import current_app, Flask, render_template, send_file, url_for
from flask_bootstrap import Bootstrap
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import redirect

from ajna_commons.flask import api_login, login
from ajna_commons.flask.user import DBUser

from ajnaapi.endpoints import ajna_api
from ajnaapi.mercanteapi import mercanteapi
from .config import Production

SWAGGER_URL = '/docs' # URL for exposing Swagger UI (without trailing '/')
API_URL = '/docs/openapi.yaml' # Our API url (can of course be a local resource)


def create_app(config_class=Production):
    app = Flask(__name__)
    app.logger.info('Criando app')
    Bootstrap(app)
    nav = Nav(app)
    csrf = CSRFProtect(app)
    # app.config['SERVER_NAME'] = 'ajna.api'
    app.secret_key = config_class.SECRET
    app.config['SECRET_KEY'] = config_class.SECRET
    app.config['mongodb'] = config_class.db
    app.config['sql'] = config_class.sql
    app.register_blueprint(ajna_api)
    csrf.exempt(ajna_api)
    app.register_blueprint(mercanteapi)
    csrf.exempt(mercanteapi)
    app.logger.info('Configurando swagger-ui...')
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    @app.route('/docs/openapi.yaml')
    def return_yaml():
        return send_file('openapi.yaml')

    app.logger.info('Configurando api login...')
    api = api_login.configure(app)
    csrf.exempt(api)

    app.logger.info('Configurando login...')
    login.configure(app)
    DBUser.dbsession = config_class.db

    app.logger.info('Configurando / e redirects')
    @nav.navigation()
    def mynavbar():
        """Menu da aplicação."""
        items = [View('Home', 'index')]
        if current_user.is_authenticated:
            items.append(View('Sair', 'commons.logout'))
        return Navbar('teste', *items)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('index.html')
        else:
            return redirect(url_for('commons.login'))
    return app
