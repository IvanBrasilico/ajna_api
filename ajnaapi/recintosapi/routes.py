from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required

from ajnaapi.mercanteapi import select_one_from_class
from ajnaapi.recintosapi.models import AcessoVeiculo
from ajnaapi.recintosapi.usecases import UseCases

recintosapi = Blueprint('recintosapi', __name__)


@recintosapi.route('/api/acessoveiculo/<id>', methods=['GET'])
@jwt_required
def get_acessoveiculo(id):
    return select_one_from_class(AcessoVeiculo,
                                 AcessoVeiculo.IdEvento,
                                 id)


@recintosapi.route('/api/acessoveiculo', methods=['POST'])
@jwt_required
def insert_acessoveiculo():
    db_session = current_app.config['db_session']
    try:
        evento_json = request.json
        recinto = '1'
        usecases = UseCases(db_session, recinto)
        acessoveiculo = usecases.insert_acessoveiculo(evento_json)
        return jsonify({'msg': 'Objeto incluído', 'id': acessoveiculo.id}), 201
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': str(err)}), 500

