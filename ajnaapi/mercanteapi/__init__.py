from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.sql import select
from sqlalchemy.engine.result import RowProxy
from integracao.mercantealchemy import (engine, conhecimentos,
                                        t_conhecimentosEmbarque)

mercanteapi = Blueprint('mercanteapi', __name__)


def dump_rowproxy(rowproxy: RowProxy, exclude: list = None):
    dump = dict([(k, v) for k, v in rowproxy.items() if not k.startswith('_')])
    if exclude:
        for key in exclude:
            if dump.get(key):
                dump.pop(key)
    return dump


@mercanteapi.route('/api/conhecimentosEmbarque/<numeroCEmercante>', methods=['GET'])
# @jwt_required
def t_conhecimento(numeroCEmercante):
    try:
        with engine.begin() as conn:
            s = select([t_conhecimentosEmbarque]).where(
                t_conhecimentosEmbarque.c.numeroCEmercante == numeroCEmercante)
            result = conn.execute(s)
            conhecimento = result.fetchone()
        if conhecimento:
            return jsonify(dump_rowproxy(conhecimento)), 200
        else:
            return jsonify({'msg': 'Conhecimento não encontrado'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentosEmbarque/new/<datainicio>', methods=['GET'])
# @jwt_required
def t_conhecimento_new(datainicio):
    try:
        with engine.begin() as conn:
            s = select([t_conhecimentosEmbarque]).where(
                t_conhecimentosEmbarque.c.creation_date >= datainicio)
            result = conn.execute(s)
            conhecimento = result.fetchone()
        if conhecimento:
            return jsonify(dump_rowproxy(conhecimento)), 200
        else:
            return jsonify({'msg': 'Conhecimento não encontrado'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentosEmbarque/list', methods=['POST'])
# @jwt_required
def t_conhecimento_list(datainicio):
    try:
        with engine.begin() as conn:
            s = select([t_conhecimentosEmbarque]).where(request.form)
            result = conn.execute(s)
            conhecimento = result.fetchone()
        if conhecimento:
            return jsonify(dump_rowproxy(conhecimento)), 200
        else:
            return jsonify({'msg': 'Conhecimento não encontrado'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def select_from_class(classe, campo, valor):
    try:
        with engine.begin() as conn:
            s = select([classe]).where(
                campo == valor)
            result = conn.execute(s).fetch_one()
        if result:
            return jsonify(dump_rowproxy(result)), 200
        else:
            return jsonify({'msg': 'Conhecimento não encontrado'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
# @jwt_required
def conhecimento_numero(numeroCEmercante):
    return select_from_class(conhecimentos,
                             conhecimentos.c.numeroCEmercante,
                             numeroCEmercante)


@mercanteapi.route('/api/jwt', methods=['GET'])
@jwt_required
def conhecimento_jwt():
    pass
