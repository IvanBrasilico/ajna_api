import datetime
from flask import (
    Blueprint, request, current_app, jsonify
)
from flask_jwt_extended import jwt_required
from ajna_commons.utils.sanitiza import mongo_sanitizar
from integracao import due_mongo

api = Blueprint('api', __name__)


@api.route('/api/grid_data', methods=['POST', 'GET'])
@jwt_required
def grid_data():
    """Executa uma consulta no banco.

    Monta um dicionário de consulta a partir dos argumentos do get.
    Se encontrar registro, retorna registro inteiro via JSON (metadados),
    o arquivo (campo content) fica em fs.chunks e é recuperado pela view
    image_id.
    """
    # TODO: Refatorar conversões de/para MongoDB - dict - JSON (Ver Bhadrasana, tem algo feito nesse sentido)
    db = current_app.config['mongodb']
    if request.method == 'POST':
        print(request.json)
        query = request.json['query']
        projection = request.json['projection']
        query_processed = {}
        for key, value in query.items():
            if isinstance(value, dict):
                value_processed = {}
                for key2, value2 in value.items():
                    try:
                        value_processed[key2] = datetime.strptime(value2, '%Y-%m-%d  %H:%M:%S')
                    except:
                        value_processed[key2] = mongo_sanitizar(value2)
                query_processed[key] = value_processed
            else:
                try:
                    query_processed[key] = datetime.strptime(value, '%Y-%m-%d  %H:%M:%S')
                except:
                    query_processed[key] = mongo_sanitizar(value)

        # logger.warning(query)
        # logger.warning(query_processed)
        # query = {mongo_sanitizar(key): mongo_sanitizar(value)
        #          for key, value in query.items()}
        # projection = {mongo_sanitizar(key): mongo_sanitizar(value)
        #          for key, value in projection.items()}
        # logger.warning(projection)
        linhas = db['fs.files'].find(query_processed, projection)
        result = []
        for linha in linhas:
            dict_linha = {}
            for key, value in linha.items():
                if isinstance(value, dict):
                    value_processed = {}
                    for key2, value2 in value.items():
                        try:
                            value_processed[key2] = datetime.strptime(value2, '%Y-%m-%d  %H:%M:%S')
                        except:
                            value_processed[key2] = str(value2)
                    dict_linha[key] = value_processed
                else:
                    try:
                        dict_linha[key] = datetime.strptime(value, '%Y-%m-%d  %H:%M:%S')
                    except:
                        dict_linha[key] = str(value)
            result.append(dict_linha)

    else:
        filtro = {mongo_sanitizar(key): mongo_sanitizar(value)
                  for key, value in request.args.items()}
        # logger.warning(filtro)
        linhas = db['fs.files'].find(filtro)
        result = [{'_id': str(linha['_id']),
                   'contentType': str(linha['metadata'].get('contentType'))
                   }
                  for linha in linhas]
    status_code = 404
    if len(result) > 0:
        status_code = 200
    return jsonify(result), status_code


@api.route('/api/dues/update', methods=['POST'])
@jwt_required
def dues_update():
    """Recebe um JSON no formato [{_id1: due1}, ..., {_idn: duen}] e grava

    """
    db = current_app.config['mongodb']
    if request.method == 'POST':
        due_mongo.update_due(db, request.json)
    return jsonify({'status': 'DUEs inseridas/atualizadas'}), 201
