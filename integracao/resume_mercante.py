"""
Após a integração dos XMLs, resumir em tabelas de Estado

Os arquivos XML possuem movimentos: 'I'nclusao, 'A'tualizacao e 'E'xclusao
Este script consolida em tabelas.


Este arquivo pode ser chamado em um prompt de comando no Servidor ou
programado para rodar via crontab, conforme exempo em /periodic_updates.sh
"""
import logging
import os
import time
import sqlalchemy
from sqlalchemy import func, select

from ajna_commons.flask.log import logger
from integracao.mercantealchemy import conhecimentos, \
    t_conhecimentosEmbarque


def execute_movimento(conn, numeroCEmercante, tipoMovimento, keys, row):
    if tipoMovimento == 'E':
        sql = conhecimentos.delete(
        ).where(conhecimentos.c.numeroCEmercante == numeroCEmercante)
        return conn.execute(sql)
    keys.remove('ID')
    keys.remove('last_modified')
    dict_campos = {key: row[key]
                   for key in keys}
    if tipoMovimento == 'I':
        sql = conhecimentos.insert()
        try:
            return conn.execute(sql, **dict_campos)
        except sqlalchemy.exc.IntegrityError:
            # TODO: Ver como resolver o problema de processar duas vezes (criar flag??)
            pass
    # tipoMovimento == 'A':
    sql = conhecimentos.update(
    ).where(conhecimentos.c.numeroCEmercante == numeroCEmercante)
    return conn.execute(sql, **dict_campos)


def processa_resumo(engine):
    with engine.begin() as conn:
        s = select([func.Max(conhecimentos.c.create_date)])
        c = conn.execute(s).fetchone()
        start_date = 0
        if c and c[0] is not None:
            start_date = c[0]
        # print(c)
        print('Start date %s' % start_date)
        s = select([t_conhecimentosEmbarque]
                   ).where(t_conhecimentosEmbarque.c.create_date >= start_date)
        cont = 0
        for row in conn.execute(s):
            cont += 1
            numeroCEmercante = row[t_conhecimentosEmbarque.c.numeroCEmercante]
            # print(numeroCEmercante)
            tipoMovimento = row[t_conhecimentosEmbarque.c.tipoMovimento]
            result_proxy = execute_movimento(conn, numeroCEmercante, tipoMovimento,
                                             conhecimentos.c.keys(), row)
        return cont


def mercante_resumo(engine):
    logger.info('Iniciando resumo da base Mercante...')
    t0 = time.time()
    cont = processa_resumo(engine)
    t = time.time()
    logger.info('%d registros processados em %0.2f' %
                (cont, t - t0)
                )


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    engine = sqlalchemy.create_engine(
        'mysql+mysqlconnector://ivan@localhost:3306/mercante')
    mercante_resumo(engine)
