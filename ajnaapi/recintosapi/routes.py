import json

from flask import Blueprint, jsonify, request, current_app, make_response
from flask_jwt_extended import jwt_required
from json2html import json2html

from ajnaapi.mercanteapi import select_one_from_class
from ajnaapi.recintosapi.models import AcessoVeiculo, PesagemVeiculo
from ajnaapi.recintosapi.usecases import UseCases

recintosapi = Blueprint('recintosapi', __name__)


@recintosapi.route('/api/acessoveiculo/<id>', methods=['GET'])
@jwt_required
def get_acessoveiculo(id):
    return select_one_from_class(AcessoVeiculo,
                                 AcessoVeiculo.id,
                                 id)


@recintosapi.route('/api/acessoveiculo', methods=['POST'])
@jwt_required
def insert_acessoveiculo():
    db_session = current_app.config['db_session']
    try:
        evento_json = request.json
        usecases = UseCases(db_session)
        acessoveiculo = usecases.insert_acessoveiculo(evento_json)
        return jsonify({'msg': 'Objeto incluído', 'id': acessoveiculo.id}), 201
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/pesagemveiculo/<id>', methods=['GET'])
@jwt_required
def get_pesagemveiculo(id):
    return select_one_from_class(PesagemVeiculo,
                                 PesagemVeiculo.id,
                                 id)


@recintosapi.route('/api/pesagemveiculo', methods=['POST'])
@jwt_required
def insert_pesagemveiculo():
    db_session = current_app.config['db_session']
    try:
        evento_json = request.json
        usecases = UseCases(db_session)
        pesagemveiculo = usecases.insert_pesagemveiculo(evento_json)
        return jsonify({'msg': 'Objeto incluído', 'id': pesagemveiculo.id}), 201
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/resumo_evento', methods=['GET'])
# @jwt_required
def resumo_evento():
    db_session = current_app.config['db_session']
    try:
        recinto = request.args['recinto']
        tipo = request.args['tipo']
        id = request.args['id']
        format = request.args.get('format', 'html')
        usecases = UseCases(db_session)
        data = usecases.load_acessoveiculo(recinto, id)
        if format == 'html':
            data = json2html.convert(data)
        elif format == 'text':
            data = {k: v for k, v in data.items() if v is not None}
            data = json.dumps(data, separators=('', ' - '), indent=2). \
                replace('{', '').replace('}', '').replace('"', '')
        response = make_response(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        response = make_response(str(err))
        response.headers['Access-Control-Allow-Origin'] = '*'
    return response
