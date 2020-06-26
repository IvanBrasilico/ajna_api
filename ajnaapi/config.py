"""Opções de configuração da aplicação."""

# import sys
# COMMONS_PATH = os.path.join('..', 'ajna_docs', 'commons')
# sys.path.insert(0, COMMONS_PATH)

from pymongo import MongoClient
from sqlalchemy import create_engine

from ajna_commons.flask.conf import MONGODB_URI, SECRET, SQL_URI
from ajna_commons.flask.log import logger


class Production:
    """Configuração do ambiente Produção."""

    TESTING = False
    SECRET = SECRET
    db = MongoClient(host=MONGODB_URI).test
    db_risco = MongoClient(host=MONGODB_URI).risco
    try:
        sql = create_engine(SQL_URI,
                            pool_size=5, max_overflow=5, pool_recycle=3600)
    except TypeError as err:
        logger.error('Erro ao conectar no Banco de Dados (config.py - Production):')
        logger.error(str(err))


class Staging:
    """Configuração do ambiente de Testes."""

    TESTING = True
    SECRET = 'fraco'  # nosec
    db = MongoClient(host=MONGODB_URI).unit_test
    db_risco = MongoClient(host=MONGODB_URI).unit_test
    sql = create_engine('sqlite://')


class Testing:
    """Configuração do ambiente de Testes."""

    TESTING = True
    SECRET = 'fraco'  # nosec
    db = MongoClient(host=MONGODB_URI).unit_test
    db_risco = MongoClient(host=MONGODB_URI).unit_test
    sql = create_engine('sqlite:///:memory:')
