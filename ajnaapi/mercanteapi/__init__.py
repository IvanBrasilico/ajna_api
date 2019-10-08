from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.sql import select
from sqlalchemy.engine.result import RowProxy
from integracao.mercantealchemy import (engine, conhecimentos,
                                        t_conhecimentosEmbarque)
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
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                campo == valor)
            result = conn.execute(s)
            # print(result.rowcount)
            if result and result.rowcount > 0:
                resultados = [dump_rowproxy(row) for row in result]
                return jsonify(resultados), 200
            else:
                return jsonify({'msg': '%s Não encontrado' % table.name}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def return_many_from_resultproxy(result):
    print(result.rowcount)
    if result and result.rowcount > 0:
        resultados = [dump_rowproxy(row) for row in result]
        return jsonify(resultados), 200
    else:
        return jsonify({'msg': 'Não encontrado'}), 404


@mercanteapi.route('/api/conhecimentosEmbarque/<numeroCEmercante>', methods=['GET'])
# @jwt_required
def t_conhecimento(numeroCEmercante):
    return select_many_from_class(t_conhecimentosEmbarque,
                                  t_conhecimentosEmbarque.c.numeroCEmercante,
                                  numeroCEmercante)


@mercanteapi.route('/api/conhecimentosEmbarque/new/<datainicio>', methods=['GET'])
# @jwt_required
def t_conhecimento_new(datainicio):
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


@mercanteapi.route('/api/conhecimentosEmbarque/list', methods=['POST'])
# @jwt_required
def t_conhecimento_list():
    try:
        with engine.begin() as conn:
            s = select([t_conhecimentosEmbarque]).where(request.form)
            result = conn.execute(s)
            if result:
                resultados = [dump_rowproxy(conhecimento) for conhecimento in result]
                return jsonify(resultados), 200
            else:
                return jsonify({'msg': 'Conhecimento não encontrado'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
# @jwt_required
def conhecimento_numero(numeroCEmercante):
    return select_one_from_class(conhecimentos,
                                 conhecimentos.c.numeroCEmercante,
                                 numeroCEmercante)


@mercanteapi.route('/api/conhecimentos/new/<datamodificacao>', methods=['GET'])
# @jwt_required
def conhecimento_new(datamodificacao):
    try:
        datamodificacao = parser.parse(datamodificacao)
        print(datamodificacao)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro no parâmetro: %s' % str(err)}), 400
    try:
        with engine.begin() as conn:
            s = select([conhecimentos]).where(
                conhecimentos.c.last_modified >= datamodificacao)
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/jwt', methods=['GET'])
@jwt_required
def conhecimento_jwt():
    pass
