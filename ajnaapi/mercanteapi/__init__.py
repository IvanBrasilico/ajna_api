from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.sql import select
from sqlalchemy.engine.result import RowProxy
from sqlalchemy.sql.expression import and_
from integracao.mercantealchemy import (conhecimentos, conteineresVazios, itens,
                                        manifestos, NCMItem, t_conhecimentosEmbarque)
from dateutil import parser

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
            return jsonify({'msg': '%s Não encontrado' % table.name}), 404
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


@mercanteapi.route('/api/conhecimentosEmbarque/<numeroCEmercante>', methods=['GET'])
@jwt_required
def t_conhecimento(numeroCEmercante):
    return select_many_from_class(t_conhecimentosEmbarque,
                                  t_conhecimentosEmbarque.c.numeroCEmercante,
                                  numeroCEmercante)


@mercanteapi.route('/api/conhecimentosEmbarque/new/<datainicio>', methods=['GET'])
@jwt_required
def t_conhecimento_new(datainicio):
    engine = current_app.config['sql']
    try:
        datainicio = parser.parse(datainicio)
        print(datainicio)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro no parâmetro: %s' % str(err)}), 400
    try:
        with engine.begin() as conn:
            s = select([t_conhecimentosEmbarque]).where(
                t_conhecimentosEmbarque.c.create_date >= datainicio)
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentosEmbarque', methods=['GET', 'POST'])
@jwt_required
def t_conhecimento_list():
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            uri_query = request.values
            lista_condicoes = [t_conhecimentosEmbarque.c[campo] == valor
                               for campo, valor in uri_query.items()]
            s = select([t_conhecimentosEmbarque]).where(and_(*lista_condicoes))
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
@jwt_required
def conhecimento_numero(numeroCEmercante):
    return select_one_from_class(conhecimentos,
                                 conhecimentos.c.numeroCEmercante,
                                 numeroCEmercante)


@mercanteapi.route('/api/conhecimentos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def conhecimento_new(datamodificacao):
    return get_datamodificacao_gt(conhecimentos, datamodificacao)


@mercanteapi.route('/api/conhecimentos', methods=['GET', 'POST'])
@jwt_required
def conhecimentos_list():
    return get_filtro(conhecimentos, request.values)


@mercanteapi.route('/api/manifestos/<numero>', methods=['GET'])
@jwt_required
def manifesto_numero(numero):
    return select_one_from_class(manifestos,
                                 manifestos.c.numero,
                                 numero)


@mercanteapi.route('/api/manifestos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def manifestos_new(datamodificacao):
    return get_datamodificacao_gt(manifestos, datamodificacao)


@mercanteapi.route('/api/manifestos', methods=['GET', 'POST'])
@jwt_required
def manifestos_list():
    return get_filtro(manifestos, request.values)


@mercanteapi.route('/api/itens/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def itens_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro(itens, query)


@mercanteapi.route('/api/itens/new/<datamodificacao>', methods=['GET'])
@jwt_required
def itens_new(datamodificacao):
    return get_datamodificacao_gt(itens, datamodificacao)


@mercanteapi.route('/api/itens', methods=['GET', 'POST'])
@jwt_required
def itens_list():
    return get_filtro(itens, request.values)


@mercanteapi.route('/api/itens/<conhecimento>', methods=['GET'])
@jwt_required
def itens_conhecimento(conhecimento):
    return select_many_from_class(itens,
                                  itens.c.numeroCEmercante,
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


@mercanteapi.route('/api/conteineresVazios/new/<datamodificacao>', methods=['GET'])
@jwt_required
def conteineresVazios_new(datamodificacao):
    return get_datamodificacao_gt(conteineresVazios, datamodificacao)


@mercanteapi.route('/api/conteineresVazios', methods=['GET', 'POST'])
@jwt_required
def conteineresVazios_list():
    return get_filtro(conteineresVazios, request.values)


@mercanteapi.route('/api/conteineresVazios/<manifesto>', methods=['GET'])
@jwt_required
def conteineresVazios_manifesto(manifesto):
    return select_many_from_class(conteineresVazios,
                                  conteineresVazios.c.manifesto,
                                  manifesto)
