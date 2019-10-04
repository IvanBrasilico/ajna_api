# import sys

# COMMONS_PATH = os.path.join('..', 'ajna_docs', 'commons')

# sys.path.insert(0, COMMONS_PATH)

from pymongo import MongoClient

from ajna_commons.flask.conf import MONGODB_URI, SECRET


class Production:
    TESTING = False
    SECRET = SECRET
    db = MongoClient(host=MONGODB_URI).test


class Testing:
    TESTING = True
    SECRET = 'fraco'  # nosec
    db = MongoClient(host=MONGODB_URI).unit_test
