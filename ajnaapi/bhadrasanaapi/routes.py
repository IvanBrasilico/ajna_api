from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required

from ajnaapi.utils import get_filtro, dump_model, get_filtro_alchemy
from bhadrasana.models.ovr import OVR, TGOVR, ItemTG
from bhadrasana.models.rvf import RVF, ImagemRVF

bhadrasanaapi = Blueprint('bhadrasanapi', __name__)


def select_one_campo_alchemy(session, model, campo, oid):
    try:
        result = session.query(model).filter(campo == oid).one_or_none()
        if result:
            return jsonify(result.dump()), 200
        else:
            return jsonify({'msg': '%s Não encontrado' % model.__class__.__name__}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def select_many_campo_alchemy(session, model, campo, valor):
    try:
        result = session.query(model).filter(campo == valor).all()
        if result:
            return jsonify([dump_model(item) for item in result]), 200
        else:
            return jsonify({'msg': '%s Não encontrado' % model.__class__.__name__}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@bhadrasanaapi.route('/api/ficha/<id>', methods=['GET'])
# @jwt_required
def ficha_id(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, OVR, OVR.id, id)


@bhadrasanaapi.route('/api/fichas', methods=['POST'])
# @jwt_required
def fichas():
    return get_filtro_alchemy(OVR, request.json)


@bhadrasanaapi.route('/api/rvf/<id>', methods=['GET'])
# @jwt_required
def rvf_id(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, RVF, RVF.id, id)


@bhadrasanaapi.route('/api/rvf', methods=['POST'])
# @jwt_required
def rvfs():
    return get_filtro_alchemy(RVF, request.json)


@bhadrasanaapi.route('/api/rvfs/<ovr_id>', methods=['GET'])
# @jwt_required
def rvfs_ovr(ovr_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, RVF, RVF.ovr_id, ovr_id)


@bhadrasanaapi.route('/api/imagens_rvf/<rvf_id>', methods=['GET'])
# @jwt_required
def imagensrvf(rvf_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, ImagemRVF, ImagemRVF.rvf_id, rvf_id)


@bhadrasanaapi.route('/api/tg/<id>', methods=['GET'])
# @jwt_required
def tg(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, RVF, RVF.id, id)


@bhadrasanaapi.route('/api/tgs/<ovr_id>', methods=['GET'])
# @jwt_required
def tgs_ovr(ovr_id):
    return select_many_campo_alchemy(TGOVR,
                                     TGOVR.ovr_id,
                                     ovr_id)


@bhadrasanaapi.route('/api/tgs', methods=['GET'])
# @jwt_required
def tgs():
    return get_filtro(RVF, request.values)


@bhadrasanaapi.route('/api/itemtg/<id>', methods=['GET'])
# @jwt_required
def iemtg(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, ItemTG, ItemTG.id, id)


@bhadrasanaapi.route('/api/itenstg/<tg_id>', methods=['GET'])
# @jwt_required
def itenstg_tg(tg_id):
    return select_many_campo_alchemy(ItemTG,
                                     ItemTG.tg_id,
                                     tg_id)


if __name__ == '__main__':
    from ajnaapi.utils import yaml_from_model

    # print(yaml_from_model(OVR))
    # print(yaml_from_model(RVF))
    # print(yaml_from_model(ImagemRVF))
    # print(yaml_from_model(EventoOVR))
    print(yaml_from_model(ItemTG))
