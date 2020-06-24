from dateutil import parser
from flask_jwt_extended import jwt_required
from sqlalchemy.engine.result import RowProxy
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_

from flask import Blueprint, current_app, jsonify, request
from virasana.integracao.mercante.mercantealchemy import Conhecimento, \
    ConteinerVazio, Item, Manifesto, NCMItem, Escala

mercanteapi = Blueprint('mercanteapi', __name__)


def dump_rowproxy(rowproxy: RowProxy, exclude: list = None):
    dump = dict([(k, v) for k, v in rowproxy.items() if not k.startswith('_')])
    if exclude:
        for key in exclude:
            if dump.get(key):
                dump.pop(key)
    return dump


def select_one_from_class(table, campo, valor):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                campo == valor)
            result = conn.execute(s).fetchone()
        if result:
            return jsonify(dump_rowproxy(result)), 200
        else:
            return jsonify({'msg': '%s Não encontrado' % table}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def select_many_from_class(table, campo, valor):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                campo == valor)
            print(campo, valor)
            result = conn.execute(s)
            if result:
                resultados = [dump_rowproxy(row) for row in result]
                if resultados and len(resultados) > 0:
                    return jsonify(resultados), 200
            return jsonify({'msg': '%s Não encontrado' % table.name}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def return_many_from_resultproxy(result):
    resultados = None
    if result:
        resultados = [dump_rowproxy(row) for row in result]
    if resultados and len(resultados) > 0:
        print(len(resultados))
        return jsonify(resultados), 200
    else:
        return jsonify({'msg': 'Não encontrado'}), 404


def get_datamodificacao_gt(table, datamodificacao):
    engine = current_app.config['sql']
    try:
        datamodificacao = parser.parse(datamodificacao)
        print(datamodificacao)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro no parâmetro: %s' % str(err)}), 400
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                table.c.last_modified >= datamodificacao)
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def get_filtro(table, uri_query):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            lista_condicoes = [table.c[campo] == valor
                               for campo, valor in uri_query.items()]
            s = select([table]).where(and_(*lista_condicoes))
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
@jwt_required
def conhecimento_numero(numeroCEmercante):
    return select_one_from_class(Conhecimento,
                                 Conhecimento.numeroCEmercante,
                                 numeroCEmercante)


@mercanteapi.route('/api/conhecimentos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def conhecimento_new(datamodificacao):
    return get_datamodificacao_gt(Conhecimento, datamodificacao)


@mercanteapi.route('/api/conhecimentos', methods=['GET', 'POST'])
@jwt_required
def conhecimentos_list():
    return get_filtro(Conhecimento, request.values)


@mercanteapi.route('/api/manifestos/<numero>', methods=['GET'])
@jwt_required
def manifesto_numero(numero):
    return select_one_from_class(Manifesto,
                                 Manifesto.numero,
                                 numero)


@mercanteapi.route('/api/manifestos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def manifestos_new(datamodificacao):
    return get_datamodificacao_gt(Manifesto, datamodificacao)


@mercanteapi.route('/api/manifestos', methods=['GET', 'POST'])
@jwt_required
def manifestos_list():
    return get_filtro(Manifesto, request.values)


@mercanteapi.route('/api/itens/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def itens_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro(Item, query)


@mercanteapi.route('/api/itens/new/<datamodificacao>', methods=['GET'])
@jwt_required
def itens_new(datamodificacao):
    return get_datamodificacao_gt(Item, datamodificacao)


@mercanteapi.route('/api/itens', methods=['GET', 'POST'])
@jwt_required
def itens_list():
    return get_filtro(Item, request.values)


@mercanteapi.route('/api/itens/<conhecimento>', methods=['GET'])
@jwt_required
def itens_conhecimento(conhecimento):
    return select_many_from_class(Item,
                                  Item.numeroCEmercante,
                                  conhecimento)


@mercanteapi.route('/api/NCMItem/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def NCMItem_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro(NCMItem, query)


@mercanteapi.route('/api/NCMItem/new/<datamodificacao>', methods=['GET'])
@jwt_required
def NCMItem_new(datamodificacao):
    return get_datamodificacao_gt(NCMItem, datamodificacao)


@mercanteapi.route('/api/NCMItem', methods=['GET', 'POST'])
@jwt_required
def NCMItem_list():
    return get_filtro(NCMItem, request.values)


@mercanteapi.route('/api/NCMItem/<conhecimento>', methods=['GET'])
@jwt_required
def NCMItem_conhecimento(conhecimento):
    return select_many_from_class(NCMItem,
                                  NCMItem.c.numeroCEmercante,
                                  conhecimento)


@mercanteapi.route('/api/ConteinerVazio/new/<datamodificacao>', methods=['GET'])
@jwt_required
def ConteinerVazio_new(datamodificacao):
    return get_datamodificacao_gt(ConteinerVazio, datamodificacao)


@mercanteapi.route('/api/ConteinerVazio', methods=['GET', 'POST'])
@jwt_required
def ConteinerVazio_list():
    return get_filtro(ConteinerVazio, request.values)


@mercanteapi.route('/api/ConteinerVazio/<manifesto>', methods=['GET'])
@jwt_required
def ConteinerVazio_manifesto(manifesto):
    return select_many_from_class(ConteinerVazio,
                                  ConteinerVazio.c.manifesto,
                                  manifesto)


@mercanteapi.route('/api/escalas/new/<datamodificacao>', methods=['GET'])
@jwt_required
def Escala_new(datamodificacao):
    return get_datamodificacao_gt(Escala, datamodificacao)


@mercanteapi.route('/api/escalas', methods=['GET', 'POST'])
@jwt_required
def Escala_list():
    return get_filtro(Escala, request.values)


@mercanteapi.route('/api/escalas/<numeroDaEscala>', methods=['GET'])
@jwt_required
def Escala_manifesto(numeroDaEscala):
    return select_many_from_class(Escala,
                                  Escala.c.numeroDaEscala,
                                  numeroDaEscala)
