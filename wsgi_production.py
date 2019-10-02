import logging
from werkzeug.wsgi import DispatcherMiddleware

from ajnaapi.main import app


gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

application = DispatcherMiddleware(app,
                                   {
                                       '/ajnaapi': app
                                   })
