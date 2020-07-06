from flask import Blueprint, current_app, jsonify

from bhadrasana.models.laudo import get_empresas, get_ncm, get_empresa

cadastrosapi = Blueprint('cadastrosapi', __name__)


@cadastrosapi.route('/api/empresas/<cnpj>', methods=['GET'])
def empresas_(cnpj):
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


@cadastrosapi.route('/api/empresa/<cnpj>', methods=['GET'])
def empresa_(cnpj):
    db_session = current_app.config['db_session']
    try:
        empresa = get_empresa(db_session, cnpj)
        if empresa is None:
            return jsonify({'msg': 'Empresa %s não encontrada' % cnpj}), 404
    except ValueError as err:
        return jsonify(
            {'msg': str(err)}), 400
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro inesperado! Detalhes no log da aplicação. ' + str(err)}), 500
    return jsonify(empresa.dump()), 200


@cadastrosapi.route('/api/ncm/<codigo>', methods=['GET'])
def ncm_(codigo):
    db_session = current_app.config['db_session']
    try:
        ncm = get_ncm(db_session, codigo)
        if ncm is None:
            return jsonify({'msg': 'NCM %s não encontrado' % codigo}), 404
    except ValueError as err:
        return jsonify(
            {'msg': str(err)}), 400
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro inesperado! Detalhes no log da aplicação. ' + str(err)}), 500
    return jsonify(ncm.dump()), 200
