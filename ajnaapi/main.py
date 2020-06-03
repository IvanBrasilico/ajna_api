"""Arquivo principal da definição da aplicação que roda a API."""
from flask import Flask, render_template, send_file, url_for, request
from flask_bootstrap import Bootstrap
from flask_jwt_extended import get_jwt_identity
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import redirect

from ajna_commons.flask import api_login, login
from ajna_commons.flask.user import DBUser
from ajnaapi.endpoints import ajna_api
from ajnaapi.mercanteapi import mercanteapi
from ajnaapi.recintosapi.routes import recintosapi
from .config import Production

SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/docs/openapi.yaml'  # Our API url (can of course be a local resource)


def create_app(config_class=Production):
    """Cria app básica e vincula todos os blueprints e módulos/extensões."""
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
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=config_class.sql))
    app.config['db_session'] = db_session
    app.register_blueprint(ajna_api)
    csrf.exempt(ajna_api)
    app.register_blueprint(mercanteapi)
    csrf.exempt(mercanteapi)
    app.register_blueprint(recintosapi)
    csrf.exempt(recintosapi)
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

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session = app.config.get('db_session')
        if db_session:
            db_session.remove()


    return app


if __name__ == '__main__':  # pragma: no cover
    app = create_app()  # pragma: no cover
    print(app.url_map)  # pragma: no cover
    app.run(port=5004)
