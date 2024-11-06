import json

from flask import Blueprint, jsonify, request, current_app, make_response
from flask_jwt_extended import jwt_required
from json2html import json2html
from sqlalchemy.orm.exc import NoResultFound

from ajnaapi.recintosapi.usecases import UseCases
from bhadrasana.routes.apirecintos import processa_zip
from bhadrasana.views import valid_file

recintosapi = Blueprint('recintosapi', __name__)


@recintosapi.route('/api/acessoveiculo/<id>', methods=['GET'])
@jwt_required
def get_acessoveiculo(id):
    db_session = current_app.config['db_session']
    try:
        usecases = UseCases(db_session)
        data = usecases.load_acessoveiculo(id=id)
        return jsonify(data), 200
    except NoResultFound:
        return jsonify({'msg': 'AcessoVeiculo %s não encontrado' % id}), 404
    except Exception as err:  # pragma: no cover
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/acessoveiculo', methods=['POST'])
@jwt_required
def insert_acessoveiculo():
    db_session = current_app.config['db_session']
    try:
        evento_json = request.json
        usecases = UseCases(db_session)
        acessoveiculo = usecases.insert_acessoveiculo(evento_json)
        return jsonify({'msg': 'Objeto incluído', 'id': acessoveiculo.id}), 201
    except Exception as err:  # pragma: no cover
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/pesagemveiculo/<id>', methods=['GET'])
@jwt_required
def get_pesagemveiculo(id):
    db_session = current_app.config['db_session']
    try:
        usecases = UseCases(db_session)
        data = usecases.load_pesagemveiculo(id=id)
        return jsonify(data), 200
    except NoResultFound:
        return jsonify({'msg': 'PesagemVeiculo %s não encontrado' % id}), 404
    except Exception as err:  # pragma: no cover
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/pesagemveiculo', methods=['POST'])
@jwt_required
def insert_pesagemveiculo():
    db_session = current_app.config['db_session']
    try:
        evento_json = request.json
        usecases = UseCases(db_session)
        pesagemveiculo = usecases.insert_pesagemveiculo(evento_json)
        return jsonify({'msg': 'Objeto incluído', 'id': pesagemveiculo.id}), 201
    except Exception as err:  # pragma: no cover
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500


@recintosapi.route('/api/resumo_evento', methods=['GET'])
@jwt_required
def resumo_evento():
    db_session = current_app.config['db_session']
    response = make_response('Erro não previsto')
    code = 500
    try:
        recinto = request.args['recinto']
        tipo = request.args['tipo']
        id = request.args['id']
        format = request.args.get('format', 'html')
        usecases = UseCases(db_session)
        if tipo == 'AcessoVeiculo':
            data = usecases.load_acessoveiculo(recinto, id)
        else:
            data = usecases.load_pesagemveiculo(recinto, id)
        if format == 'html':
            data = json2html.convert(data)
        elif format == 'text':
            data = {k: v for k, v in data.items() if v is not None}
            data = json.dumps(data, separators=('', ' - '), indent=2). \
                replace('{', '').replace('}', '').replace('"', '')
        response = make_response(data)
        code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'
    except Exception as err:  # pragma: no cover
        current_app.logger.error(err, exc_info=True)
        response = make_response(str(err))
        response.headers['Access-Control-Allow-Origin'] = '*'
    return response, code




@recintosapi.route('/api/upload_arquivo_json_api', methods=['POST'])
@jwt_required
#@login_required
def upload_arquivo_json_api_api():
    # Upload de arquivo API Recintos - JSON API Friendly
    session = current_app.config.get('dbsession')
    try:
        file = request.files.get('file')
        validfile, mensagem = valid_file(file, extensions=['zip'])
        if not validfile:
            return jsonify({'msg': 'Arquivo "file" vazio ou não incluído no POST'}, 404)
        processa_zip(file, session)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg:': str(err)}, 500)
    return jsonify({'msg': 'Arquivo integrado com sucesso!!'}, 200)
