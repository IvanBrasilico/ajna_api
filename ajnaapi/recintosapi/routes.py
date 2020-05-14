from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ajnaapi.mercanteapi import select_one_from_class
from ajnaapi.recintosapi.models import AcessoVeiculo

recintosapi = Blueprint('recintosapi', __name__)


@recintosapi.route('/api/acessoveiculo/<id>', methods=['GET'])
@jwt_required
def acessoveiculo(id):
    return select_one_from_class(AcessoVeiculo,
                                 AcessoVeiculo.IdEvento,
                                 id)

