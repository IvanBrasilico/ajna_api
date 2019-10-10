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
from integracao.mercantealchemy import conhecimentos, manifestos, \
    t_conhecimentosEmbarque, t_manifestosCarga


def execute_movimento(conn, destino, chave, valor_chave,
                      tipoMovimento, keys, row):
    if tipoMovimento == 'E':
        sql = destino.delete(
        ).where(chave == valor_chave)
        return conn.execute(sql)
    keys.remove('ID')
    keys.remove('last_modified')
    dict_campos = {key: row[key]
                   for key in keys}
    if tipoMovimento == 'I':
        sql = destino.insert()
        try:
            return conn.execute(sql, **dict_campos)
        except sqlalchemy.exc.IntegrityError:
            # TODO: Ver como resolver o problema de processar duas vezes (criar flag??)
            pass
    # tipoMovimento == 'A':
    sql = destino.update(
    ).where(chave == valor_chave)
    return conn.execute(sql, **dict_campos)


def processa_resumo(engine, origem, destino, chave):
    with engine.begin() as conn:
        s = select([func.Max(destino.c.create_date)])
        c = conn.execute(s).fetchone()
        start_date = 0
        if c and c[0] is not None:
            start_date = c[0]
        # print(c)
        print('Start date %s' % start_date)
        s = select([origem]
                   ).where(origem.c.create_date >= start_date)
        cont = 0
        for row in conn.execute(s):
            cont += 1
            valor_chave = row[chave]
            # print(numeroCEmercante)
            tipoMovimento = row[origem.c.tipoMovimento]
            result_proxy = execute_movimento(conn, destino, chave, valor_chave,
                                             tipoMovimento, destino.c.keys(), row)
        return cont


def mercante_resumo(engine):
    logger.info('Iniciando resumo da base Mercante...')
    t0 = time.time()
    migracoes = {t_conhecimentosEmbarque: conhecimentos,
                 t_manifestosCarga: manifestos}
    chaves = {conhecimentos: 'numeroCEmercante',
              manifestos: 'numeroManifesto'}
    for origem, destino in migracoes.items():
        cont = processa_resumo(engine, origem, destino, chaves[destino])
    t = time.time()
    logger.info('%d registros processados em %0.2f' %
                (cont, t - t0)
                )


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    engine = sqlalchemy.create_engine(
        'mysql+pymysql://ivan@localhost:3306/mercante')
    mercante_resumo(engine)
