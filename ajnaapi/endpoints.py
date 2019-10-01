import datetime
from base64 import b64encode
from collections import OrderedDict

from flask import (
    Blueprint, request, current_app, jsonify
)
from flask_jwt_extended import jwt_required

from ajna_commons.utils.images import mongo_image
from ajna_commons.utils.sanitiza import mongo_sanitizar
from integracao import due_mongo

ajna_api = Blueprint('ajna_api', __name__)


@ajna_api.route('/api/grid_data', methods=['POST', 'GET'])
@jwt_required
def api_grid_data():
    """Executa uma consulta no banco.

    Monta um dicionário de consulta a partir dos argumentos do get.
    Se encontrar registro, retorna registro inteiro via JSON (metadados),
    o arquivo (campo content) fica em fs.chunks e é recuperado pela view
    image_id.
    """
    # TODO: Refatorar conversões de/para MongoDB - dict - JSON (Ver Bhadrasana, tem algo feito nesse sentido)
    db = current_app.config['mongodb']
    try:
        if request.method == 'POST':
            print(request.json)
            current_app.logger.info(request.json)
            query = request.json['query']
            projection = request.json.get('projection')
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

            linhas = db['fs.files'].find(query_processed, projection).limit(100)
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
            linhas = db['fs.files'].find(filtro).limit(100)
            result = [{'_id': str(linha['_id']),
                       'contentType': str(linha['metadata'].get('contentType'))
                       }
                      for linha in linhas]
        status_code = 404
        if len(result) > 0:
            status_code = 200
        return jsonify(result), status_code
    except Exception as err:
        return jsonify({'msg': 'Erro: %s' % str(err)}), 400


@ajna_api.route('/api/dues/update', methods=['POST'])
@jwt_required
def dues_update():
    """Recebe um JSON no formato [{_id1: due1}, ..., {_idn: duen}] e grava

    """
    # FIXME: Sanitizar esta entrada tbm
    db = current_app.config['mongodb']
    try:
        if request.method == 'POST':
            due_mongo.update_due(db, request.json)
        return jsonify({'msg': 'DUEs inseridas/atualizadas'}), 201
    except Exception as err:
        return jsonify({'msg': 'Erro inesperado: %s ' % str(err)}), 400


@ajna_api.route('/api/summary_aniita/<ce_mercante>', methods=['POST', 'GET'])
@jwt_required
def api_summary(ce_mercante):
    db = current_app.config['mongodb']
    ce_mercante = mongo_sanitizar(ce_mercante)
    print('Consultando CE-Mercante %s' % ce_mercante)
    try:
        cursor = db.fs.files.find({'metadata.carga.conhecimento.conhecimento': ce_mercante})
        summary = []
        print('Consultou!!!')
        for linha in cursor:
            registro = OrderedDict()
            registro['imagem'] = str(linha['_id'])
            metadata = linha.get('metadata')
            carga = metadata.get('carga')
            predictions = metadata.get('predictions')
            registro['Numero Container'] = metadata.get('numeroinformado')
            registro['Data Escaneamento'] = datetime.datetime.strftime(
                metadata.get('dataescaneamento'), '%d/%m/%Y %H:%M')
            if predictions:
                peso = predictions[0].get('peso')
                if peso and isinstance(peso, float):
                    registro['Peso estimado imagem'] = '{:0.2f}'.format(peso)
            conteiner = carga.get('container')
            if isinstance(conteiner, list):
                conteiner = conteiner[0]
            tara = conteiner.get('taracontainer', '0')
            tara = float(tara.replace(',', '.'))
            peso = conteiner.get('pesobrutoitem', '0')
            peso = float(peso.replace(',', '.'))
            volume = conteiner.get('volumeitem')
            volume = float(volume.replace(',', '.'))
            registro['Peso bruto declarado'] = peso
            registro['Tara declarada'] = tara
            registro['Volume declarado'] = volume
            registro['NCM'] = ' '.join(set([ncm.get('ncm')
                                            for ncm in carga.get('ncm')]))
            manifesto = carga.get('manifesto')
            if isinstance(manifesto, list):
                manifesto = manifesto[0]
            registro['Manifesto Mercante'] = manifesto.get('manifesto')
            registro['Tipo Manifesto'] = manifesto.get('tipomanifesto')
            conhecimento = carga.get('conhecimento')
            if isinstance(conhecimento, list):
                conhecimento = conhecimento[0]
            registro['NIC CE Mercante'] = conhecimento.get('conhecimento')
            registro['Tipo CE Mercante'] = conhecimento.get('tipo')
            registro['Descricao mercadoria CE Mercante'] = \
                conhecimento.get('descricaomercadoria')
            if manifesto.get('tipomanifesto') != 'lce':
                registro['Consignatario carga'] = \
                    '%s - %s ' % (conhecimento.get('cpfcnpjconsignatario'),
                                  conhecimento.get('nomeconsignatario'))
            summary.append(registro)
        status_code = 404
        if len(summary) > 0:
            status_code = 200
        return jsonify(summary), status_code
    except Exception as err:
        raise (err)
        current_app.logger.error(err)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@ajna_api.route('/api/image/<_id>', methods=['POST', 'GET'])
@jwt_required
def api_image(_id):
    db = current_app.config['mongodb']
    _id = mongo_sanitizar(_id)
    image = mongo_image(db, _id)
    if image:
        return jsonify(dict(
            content=b64encode(image).decode(),
            mimetype='image/jpeg'
        )), 200
    return jsonify({}), 404
