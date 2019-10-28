"""
Definição dos códigos que são rodados para integração dos XMLs do Mercante.

Este arquivo pode ser chamado em um prompt de comando no Servidor ou
programado para rodar via crontab, conforme exempo em /periodic_updates.sh
"""
import logging
import os
import time
import pandas as pd
import requests
from datetime import datetime

from collections import Counter
from xml.etree import ElementTree

from ajna_commons.flask.log import logger
from integracao.mercante import mercante, mercantealchemy
from ajnaapi.config import Staging
from integracao.mercante.mercantealchemy import data_ultimo_arquivo_processado

FORMATO_DATA = '%y%m%d%H%M%S'
URL_ANIITA_LISTA = ''
URL_ANIITA_DOWNLOAD = ''
DESTINO_ARQUIVOS = 'mercante'


def get_arquivos_novos():
    """Baixa arquivos novos da API do Aniita"""
    data_ultimo_arquivo = data_ultimo_arquivo_processado()
    datainicial = datetime.strftime(data_ultimo_arquivo, FORMATO_DATA)
    datafinal = datetime.strftime(datetime.now(), FORMATO_DATA)
    print(datainicial, datafinal)
    r = requests.get(URL_ANIITA_LISTA, data={'datainicial': datainicial,
                                             'datafinal': datafinal})
    lista_arquivos = r.json()
    for filename in lista_arquivos:
        r = requests.get(URL_ANIITA_DOWNLOAD, filename)
        destino = os.path.join(DESTINO_ARQUIVOS, filename)
        with open(destino, 'wb') as out:
            out.write(r.content)
    

def processa_classes(engine, lista_arquivos):
    count_objetos = Counter()
    lista_erros = []
    for arquivo in lista_arquivos:
        xtree = ElementTree.parse(os.path.join(mercante.MERCANTE_DIR, arquivo))
        xroot = xtree.getroot()
        objetos = []
        for node in xroot:
            classe = mercante.classes.get(node.tag)
            if classe:
                count_objetos[classe] += 1
                objeto = classe()
                objeto._parse_node(node)
                objetos.append(objeto._to_dict())
        df = pd.DataFrame(objetos)
        try:
            df.to_sql(node.tag, engine, if_exists='append')
        except Exception as err:
            logger.error('Erro ocorrido no arquivo %s. %s' % (arquivo, err))
            lista_erros.append(arquivo)
    return count_objetos, lista_erros


def processa_classes_em_lista(engine, lista_arquivos):
    count_objetos = Counter()
    lista_erros = []
    for arquivo in lista_arquivos:
        xtree = ElementTree.parse(os.path.join(mercante.MERCANTE_DIR, arquivo))
        xroot = xtree.getroot()
        objetos = []
        for node in xroot:
            classe = mercante.classes_em_lista.get(node.tag)
            if classe:
                classe_pai = mercante.classes.get(node.tag)
                objeto_pai = classe_pai()
                objeto_pai._parse_node(node)
                tag_classe = classe._tag
                for subnode in node.findall(tag_classe):
                    count_objetos[classe] += 1
                    objeto = classe(objeto_pai)
                    objeto._parse_node(subnode)
                    objetos.append(objeto._to_dict())
        if objetos and len(objetos) > 0:
            df = pd.DataFrame(objetos)
            classname = objeto.__class__.__name__
            try:
                df.to_sql(classname, engine, if_exists='append')
            except Exception as err:
                logger.error('Erro ocorrido no arquivo %s. %s' % (arquivo, err))
                lista_erros.append(arquivo)
    return count_objetos, lista_erros


def xml_para_mercante(engine, lote=100):
    logger.info('Iniciando atualizações da base Mercante...')
    lista_arquivos = \
        [f for f in os.listdir(mercante.MERCANTE_DIR)
         if os.path.isfile(os.path.join(mercante.MERCANTE_DIR, f))]
    # print(lista_arquivos)
    lista_arquivos = lista_arquivos[:lote]
    t0 = time.time()
    count_objetos, lista_erros = processa_classes(engine, lista_arquivos)
    t = time.time()
    logger.info('%d arquivos processados com %d objetos em %0.2f s' %
                (len(lista_arquivos), sum(count_objetos.values()), t - t0)
                )
    logger.info(str(count_objetos.most_common()))
    t0 = time.time()
    count_objetos_lista, lista_erros_lista = processa_classes_em_lista(engine,
                                                                       lista_arquivos)
    t = time.time()
    logger.info('%d arquivos processados com %d lista de objetos em %0.2f s' %
                (len(lista_arquivos), sum(count_objetos_lista.values()), t - t0)
                )
    logger.info(str(count_objetos_lista.most_common()))
    arquivoscomerro = set([*lista_erros, *lista_erros_lista])
    logger.info('%d Arquivos com erro sendo copiados para diretório erro ' %
                len(arquivoscomerro)
                )
    for arquivo in arquivoscomerro:
        os.rename(os.path.join(mercante.MERCANTE_DIR, arquivo),
                  os.path.join(mercante.MERCANTE_DIR, 'erros', arquivo))
    lista_arquivos_semerro = [arquivo for arquivo in lista_arquivos
                              if arquivo not in arquivoscomerro]
    logger.info('%d Arquivos SEM erro sendo copiados para diretório processados ' %
                len(lista_arquivos_semerro)
                )
    for arquivo in lista_arquivos_semerro:
        os.rename(os.path.join(mercante.MERCANTE_DIR, arquivo),
                  os.path.join(mercante.MERCANTE_DIR, 'processados', arquivo))


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    # engine = sqlalchemy.create_engine('mysql+pymysql://ivan@localhost:3306/mercante')
    engine = Staging.sql
    xml_para_mercante(engine)
