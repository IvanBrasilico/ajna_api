from flask import Blueprint, current_app, jsonify

from bhadrasana.models.laudo import get_empresas

cadastrosapi = Blueprint('cadastrosapi', __name__)


@cadastrosapi.route('/api/empresa/<cnpj>', methods=['GET'])
def ficha_id(cnpj):
    db_session = current_app.config['db_session']
    try:
        empresas = get_empresas(db_session, cnpj)
        result = [empresa.dump() for empresa in empresas]
    except ValueError as err:
        return jsonify(
            {'msg': str(err)}), 400
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro inesperado! Detalhes no log da aplicação. ' + str(err)}), 500
    return jsonify(result), 404 if len(result) == 0 else 200
