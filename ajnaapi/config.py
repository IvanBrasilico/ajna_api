# import sys

# COMMONS_PATH = os.path.join('..', 'ajna_docs', 'commons')

# sys.path.insert(0, COMMONS_PATH)

from ajna_commons.flask.conf import MONGODB_URI, SECRET
from pymongo import MongoClient


class Production:
    TESTING = False
    SECRET = SECRET
    db = MongoClient(host=MONGODB_URI).test

class Testing:
    TESTING = True
    SECRET = 'fraco'
    db = MongoClient(host=MONGODB_URI).unit_test
