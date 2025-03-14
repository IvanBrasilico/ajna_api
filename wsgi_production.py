import sys
sys.path.append('.')
sys.path.insert(0, '../ajna_docs/commons')
sys.path.insert(0, '../ajna_api')
sys.path.insert(0, '../virasana')
sys.path.insert(0, '../bhadrasana2')
import logging
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from ajnaapi.main import create_app


app = create_app()  # pragma: no cover
print(app.url_map)  # pragma: no cover

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

application = DispatcherMiddleware(app,
                                   {
                                       '/ajnaapi': app
                                   })


if __name__ == '__main__':
    run_simple('localhost', 5004, application, use_reloader=True)
