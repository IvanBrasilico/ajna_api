"""Endpoints para integração de clientes e sistemas com os dados do AJNA."""
import datetime
import json
from base64 import b64encode
from collections import OrderedDict

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ajna_commons.utils.images import mongo_image
from ajna_commons.utils.sanitiza import mongo_sanitizar
from ajnaapi.carga_mongo import CargaLoader

ajna_api = Blueprint('ajnaapi', __name__)


def converte_ids(adict: dict):
    _id = adict.get('_id')
    if _id:
        # print('Convertendo id ', _id)
        adict['_id'] = str(_id)
    for key, value in adict.items():
        if isinstance(value, dict):
            # print('*****', key, value, type(value))
            converte_ids(value)
        if isinstance(value, list):
            # print('*****', key, value, type(value))
            for item in value:
                # print('XXXXXXXXXXXXXXX', item, type(item))
                converte_ids(item)


@ajna_api.route('/api/grid_data', methods=['POST', 'GET'])
@jwt_required
def api_grid_data():
    """Executa uma consulta no banco.

    Monta um dicionário de consulta a partir dos argumentos do get.
    Se encontrar registro, retorna registro inteiro via JSON (metadados),
    o arquivo (campo content) fica em fs.chunks e é recuperado pela view
    image_id.
    """
    # TODO: Refatorar conversões de/para MongoDB - dict - JSON
    #  (Ver Bhadrasana, tem algo feito nesse sentido)
    db = current_app.config['mongodb']
    result = []
    try:
        if request.method == 'POST':
            try:
                current_app.logger.info('grid_data request_data ' + str(request.data))
                if request.is_json:
                    request_dict = request.get_json()
                else:
                    request_dict = request.form
                current_app.logger.info(str(type(request.json)) + str(request.json))
            except Exception as err:
                request_dict = {}
                current_app.logger.error(str(err))
                current_app.logger.error(request.data)
            if isinstance(request_dict, str):
                try:
                    request_dict = request_dict.replace('\'', '"')
                    request_dict = json.loads(request_dict)
                except Exception as err:
                    request_dict = {}
                    current_app.logger.error(str(err))
            query = request_dict['query']
            projection = request_dict.get('projection')
            query_processed = {}
            for key, value in query.items():
                if isinstance(value, dict):
                    value_processed = {}
                    for key2, value2 in value.items():
                        if isinstance(value2, str):
                            try:
                                value_processed[key2] = \
                                    datetime.datetime.strptime(value2,
                                                               '%Y-%m-%d  %H:%M:%S')
                            except Exception:  # TODO: See specific exception
                                value_processed[key2] = mongo_sanitizar(value2)
                        else:
                            value_processed[key2] = value2
                    query_processed[key] = value_processed
                else:
                    try:
                        query_processed[key] = \
                            datetime.datetime.strptime(value, '%Y-%m-%d  %H:%M:%S')
                    except Exception:
                        query_processed[key] = mongo_sanitizar(value)
            current_app.logger.info(query)
            current_app.logger.info(query_processed)
            current_app.logger.info(projection)
            # TODO: limit and skip
            linhas = db['fs.files'].find(query_processed, projection).limit(1000)
            result = list(linhas)
            # current_app.logger.warning(result)
            # print(result)
            for linha in result:
                converte_ids(linha)
            # print(result)
        else:
            current_app.logger.warning(
                'Filtro %s' % {key: value
                               for key, value in request.args.items()})
            filtro = {mongo_sanitizar(key): mongo_sanitizar(value)
                      for key, value in request.args.items()}
            current_app.logger.warning('Filtro %s' % filtro)
            linhas = db['fs.files'].find(filtro).limit(1000)
            for linha in linhas:
                result.append({'_id': str(linha['_id']),
                               'contentType': str(linha['metadata'].get('contentType'))
                               })
        if len(result) > 0:
            return jsonify(result), 200
        return jsonify({}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        current_app.logger.error(request.data)
        return jsonify({'msg': 'Erro: %s' % err}), 400


@ajna_api.route('/api/summary_aniita/<ce_mercante>', methods=['GET'])
@jwt_required
def api_summary(ce_mercante):
    """Fornece um sumário dos dados para visualização."""
    db = current_app.config['mongodb']
    loader = CargaLoader()
    ce_mercante = mongo_sanitizar(ce_mercante)
    # print('Consultando CE-Mercante %s' % ce_mercante)
    try:
        cursor = db.fs.files.find(
            {'metadata.carga.conhecimento.conhecimento': ce_mercante}
        )
        summary = []
        registro_pai = OrderedDict()
        # print('Consultou!!!')
        ind = 0
        for linha in cursor:
            metadata = linha.get('metadata')
            carga = metadata.get('carga')
            predictions = metadata.get('predictions')
            carga_load = loader.load_from_gridfs(linha)
            if ind == 0:
                manifesto = carga_load.manifestos[0]
                registro_pai['Manifesto Mercante'] = manifesto.manifesto
                registro_pai['Tipo Manifesto'] = manifesto.tipomanifesto
                conhecimento = carga.get('conhecimento')
                if isinstance(conhecimento, list):
                    conhecimento = conhecimento[0]
                registro_pai['NIC CE Mercante'] = conhecimento.get('conhecimento')
                registro_pai['Tipo CE Mercante'] = conhecimento.get('tipo')
                registro_pai['Descricao mercadoria CE Mercante'] = \
                    conhecimento.get('descricaomercadoria')
                if manifesto.tipomanifesto != 'lce':
                    registro_pai['Consignatario carga'] = \
                        '%s - %s ' % (conhecimento.get('cpfcnpjconsignatario'),
                                      conhecimento.get('nomeconsignatario'))
                ind = 1
            registro = OrderedDict()
            registro['imagem'] = str(linha['_id'])
            registro['Numero Container'] = metadata.get('numeroinformado')
            try:
                registro['Data Escaneamento'] = datetime.datetime.strftime(
                    metadata.get('dataescaneamento'), '%d/%m/%Y %H:%M')
            except Exception as err:
                current_app.logger.error(err, exc_info=True)
                registro['Data Escaneamento'] = str(err)
            if predictions:
                peso = predictions[0].get('peso')
                if peso and isinstance(peso, float):
                    registro['Peso estimado imagem'] = '{:0.2f}'.format(peso)
            conteiner = carga.get('container')
            if isinstance(conteiner, list):
                conteiner = conteiner[0]
            for campo in ['taracontainer', 'pesobrutoitem', 'volumeitem']:
                try:
                    valor_str = conteiner.get(campo, '0')
                    registro[campo] = float(valor_str.replace(',', '.'))
                except Exception as err:
                    current_app.logger.error(err, exc_info=True)
                    registro[campo] = str(err)
            registro['NCM'] = ' '.join(set([ncm.get('ncm')
                                            for ncm in carga.get('ncm')]))
            summary.append(registro)
        status_code = 404
        if len(summary) > 0:
            status_code = 200
            registro_pai['Containers'] = summary
        return jsonify(registro_pai), status_code
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@ajna_api.route('/api/image/<_id>', methods=['GET'])
@ajna_api.route('/api/image_risco/<_id>', methods=['GET'])
@jwt_required
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
            return jsonify(dict(
                content=b64encode(image).decode(),
                mimetype='image/jpeg'
            )), 200
        return jsonify({}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400
