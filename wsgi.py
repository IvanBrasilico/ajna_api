import logging
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from ajnaapi.main import create_app

from ajna_commons.flask.user import DBUser
from ajnaapi.config import Testing

app = create_app(Testing)  # pragma: no cover Testing = SQLite
DBUser.dbsession = None  # Aceita autenticação fake (qqer username==password)

gunicorn_logger = logging.getLogger('gunicorn.debug')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

application = DispatcherMiddleware(app,
                                   {
                                       '/ajnaapi': app
                                   })

if __name__ == '__main__':
    print(app.url_map)  # pragma: no cover
    run_simple('localhost', 5004, application, use_reloader=True)
    # app.run(port=5004, threaded=False, debug=True)
