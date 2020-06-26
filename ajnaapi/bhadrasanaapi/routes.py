from flask_jwt_extended import jwt_required

from flask import Blueprint, request, current_app, jsonify

from ajnaapi.utils import select_one_from_class, select_many_from_class, get_filtro, dump_model
from bhadrasana.models.ovr import OVR
from bhadrasana.models.rvf import RVF, ImagemRVF


bhadrasanaapi = Blueprint('bhadrasanapi', __name__)


@bhadrasanaapi.route('/api/fichas/<id>', methods=['GET'])
# @jwt_required
def ficha_id(id):
    session = current_app.config['db_session']
    try:
        result = session.query(OVR).filter(OVR.id == id).one_or_none()
        if result:
            return jsonify(dump_model(result)), 200
        else:
            return jsonify({'msg': '%s Não encontrado' % 'OVR'}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


@bhadrasanaapi.route('/api/fichas', methods=['GET'])
# @jwt_required
def fichas():
    return get_filtro(OVR, request.values)


@bhadrasanaapi.route('/api/rvf/<id>', methods=['GET'])
# @jwt_required
def rvf_id(id):
    return select_one_from_class(RVF,
                                 RVF.id,
                                 id)

@bhadrasanaapi.route('/api/rvf', methods=['GET'])
# @jwt_required
def rvfs():
    return get_filtro(RVF, request.values)


@bhadrasanaapi.route('/api/imagens_rvf/<rvf_id>', methods=['GET'])
# @jwt_required
def imagensrvf(rvf_id):
    return select_one_from_class(ImagemRVF,
                                 ImagemRVF.rvf_id,
                                 rvf_id)




if __name__ == '__main__':
    from ajnaapi.utils import yaml_from_model
    print(yaml_from_model(OVR))
    print(yaml_from_model(RVF))
    print(yaml_from_model(ImagemRVF))
