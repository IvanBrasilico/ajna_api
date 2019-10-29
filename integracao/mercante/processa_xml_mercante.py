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
import sqlalchemy
from datetime import datetime, timedelta

from collections import Counter
from xml.etree import ElementTree

from ajna_commons.flask.log import logger
from integracao.mercante import mercante
# from ajnaapi.config import Staging
from integracao.mercante.mercantealchemy import data_ultimo_arquivo_processado, \
    grava_arquivo_processado

FORMATO_DATA_ANIITA = '%y%m%d%H%M%S'
FORMATO_DATA_ARQUIVO = '%y-%m-%d%-H-%-M-%S'
URL_ANIITA_LISTA = 'http://10.50.13.17:8443/consultaArquivos'
URL_ANIITA_DOWNLOAD = 'http://10.50.13.17:8443/download'


def get_arquivos_novos(engine):
    """Baixa arquivos novos da API do Aniita"""
    data_ultimo_arquivo = data_ultimo_arquivo_processado(engine)
    datainicial = datetime.strftime(data_ultimo_arquivo, FORMATO_DATA_ANIITA)
    datafinal = datetime.strftime(data_ultimo_arquivo + timedelta(days = 1),
                                  FORMATO_DATA_ANIITA)
    print(datainicial, datafinal)
    r = requests.get(URL_ANIITA_LISTA, params={'dtInicial': datainicial,
                                             'dtFinal': datafinal})
    print(r.url)
    print(r.text)
    lista_arquivos = r.json()
    for filename in lista_arquivos:
        r = requests.get(URL_ANIITA_DOWNLOAD, params={'nome': filename})
        print(r.url)
        destino = os.path.join(mercante.MERCANTE_DIR, filename)
        print('Gerando arquivo %s' % destino)
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
    logger.info('Baixando arquivos novos...')
    get_arquivos_novos(engine)
    logger.info('Iniciando atualizações da base Mercante...')
    lista_arquivos = \
        [f for f in os.listdir(mercante.MERCANTE_DIR)
         if os.path.isfile(os.path.join(mercante.MERCANTE_DIR, f))]
    # print(lista_arquivos)
    lista_arquivos = sorted(lista_arquivos)
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
    # Grava em tabela arquivos processados
    for arquivo in lista_arquivos:
        ind_partedata = arquivo.rfind('_', )
        partedata = arquivo[ind_partedata:-4]
        try:
            data = datetime.strptime(partedata, FORMATO_DATA_ARQUIVO)
        except ValueError as err:
            data = 0.
            print(err)
        grava_arquivo_processado(engine, arquivo, data)
    # Tira arquivos processados do path
    for arquivo in arquivoscomerro:
        os.rename(os.path.join(mercante.MERCANTE_DIR, arquivo),
                  os.path.join(mercante.MERCANTE_DIR, 'erros', arquivo))
    lista_arquivos_semerro = [arquivo for arquivo in lista_arquivos
                              if arquivo not in arquivoscomerro]
    logger.info('%d Arquivos SEM erro sendo copiados para diretório processados ' %
                len(lista_arquivos_semerro)
                )
    # Tira arquivos com erro do path
    for arquivo in lista_arquivos_semerro:
        os.rename(os.path.join(mercante.MERCANTE_DIR, arquivo),
                  os.path.join(mercante.MERCANTE_DIR, 'processados', arquivo))


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    # engine = sqlalchemy.create_engine('mysql+pymysql://ivan@localhost:3306/mercante')
    # engine = Staging.sql
    engine = sqlalchemy.create_engine('sqlite:///teste.db')
    xml_para_mercante(engine)
