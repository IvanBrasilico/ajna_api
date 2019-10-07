"""
Definição dos códigos que são rodados para integração dos XMLs do Mercante.

Este arquivo pode ser chamado em um prompt de comando no Servidor ou
programado para rodar via crontab, conforme exempo em /periodic_updates.sh
"""
import logging
import os
import sys
import time

import sqlalchemy

from ajna_commons.flask.log import logger
from processa_xml_mercante import mercante_updates

def mercante_periodic(connection):
    print('Iniciando atualizações...')
    mercante_updates(connection)


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    with sqlalchemy.create_engine(
            'mysql+mysqlconnector://ivan@localhost:3306/mercante') as connection:
        daemonize = '--daemon' in sys.argv
        s0 = time.time() - 600
        mercante_periodic(connection)
        counter = 1
        while daemonize:
            logger.info('Dormindo 10 minutos... ')
            logger.info('Tempo decorrido %s segundos.' % (time.time() - s0))
            time.sleep(30)
            if time.time() - s0 > 600:
                logger.info('Periódico chamado rodada %s' % counter)
                counter += 1
                mercante_periodic(connection)
                s0 = time.time()
