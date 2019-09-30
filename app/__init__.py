from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import redirect

from ajna_commons.flask import api_login, login
from app.endpoints import api
from .config import Production


def create_app(config_class=Production):
    app = Flask(__name__)
    Bootstrap(app)
    nav = Nav(app)
    csrf = CSRFProtect(app)
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

    # app.config['SERVER_NAME'] = 'ajna.api'
    app.secret_key = config_class.SECRET
    app.config['mongodb'] = config_class.db
    api = api_login.configure(app)
    login.configure(app)
    app.register_blueprint(api)
    csrf.exempt(api)
    return app
