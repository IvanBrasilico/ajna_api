"""Endpoints para integração de clientes e sistemas com os dados do AJNA."""

from flask import Blueprint, current_app, jsonify, request, Response
from flask_jwt_extended import jwt_required

from ajna_commons.utils.images import mongo_image
from ajna_commons.utils.sanitiza import mongo_sanitizar
from virasana.integracao.due import due_mongo

ajna_api = Blueprint('ajnaapi', __name__)


@ajna_api.route('/api/image/<_id>', methods=['GET'])
@ajna_api.route('/api/image_risco/<_id>', methods=['GET'])
# @jwt_required
def api_image(_id):
    if 'risco' in request.url:
        db = current_app.config['mongodb_risco']
    else:
        db = current_app.config['mongodb']
    _id = mongo_sanitizar(_id)
    try:
        current_app.logger.warning(_id)
        image = mongo_image(db, _id)
        if image:
            # return jsonify(dict(content=b64encode(image).decode(),
            #                    mimetype='image/jpeg')), 200
            return Response(response=image, mimetype='image/jpeg')
        return jsonify({}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@ajna_api.route('/api/dues/update', methods=['POST'])
@jwt_required
def dues_update():
    """Recebe um JSON no formato [{_id1: due1}, ..., {_idn: duen}] e grava."""
    db = current_app.config['mongodb']
    if request.method == 'POST':
        due_mongo.update_due(db, request.json)
    return jsonify({'status': 'DUEs inseridas/atualizadas'}), 201
