from datetime import datetime

from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required

from ajnaapi.utils import get_filtro_alchemy, dump_model
from ajnaapi.utils import select_one_campo_alchemy, select_many_campo_alchemy
from bhadrasana.forms.exibicao_ovr import ExibicaoOVR, TipoExibicao
from bhadrasana.models import get_usuario_telegram
from bhadrasana.models.laudo import get_empresa, get_sats_cnpj
from bhadrasana.models.ovr import OVR, TGOVR, ItemTG
from bhadrasana.models.ovrmanager import get_ovr_responsavel, get_ovr_empresa
from bhadrasana.models.riscomanager import consulta_container_objects
from bhadrasana.models.rvf import RVF, ImagemRVF
from bhadrasana.models.virasana_manager import get_dues_empresa, \
    get_ces_empresa, get_detalhes_mercante

bhadrasanaapi = Blueprint('bhadrasanapi', __name__)


@bhadrasanaapi.route('/api/ficha/<id>', methods=['GET'])
@jwt_required
def ficha_id(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, OVR, OVR.id, id)


@bhadrasanaapi.route('/api/fichas', methods=['POST'])
@jwt_required
def fichas():
    return get_filtro_alchemy(OVR, request.json)


@bhadrasanaapi.route('/api/rvf/<id>', methods=['GET'])
@jwt_required
def rvf_id(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, RVF, RVF.id, id)


@bhadrasanaapi.route('/api/rvfs', methods=['POST'])
@jwt_required
def rvfs():
    return get_filtro_alchemy(RVF, request.json)


@bhadrasanaapi.route('/api/rvfs/<ovr_id>', methods=['GET'])
@jwt_required
def rvfs_ovr(ovr_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, RVF, RVF.ovr_id, ovr_id)


@bhadrasanaapi.route('/api/imagens_rvf/<rvf_id>', methods=['GET'])
@jwt_required
def imagensrvf(rvf_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, ImagemRVF, ImagemRVF.rvf_id, rvf_id)


@bhadrasanaapi.route('/api/tg/<id>', methods=['GET'])
@jwt_required
def tg(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, TGOVR, TGOVR.id, id)


@bhadrasanaapi.route('/api/tgs/<ovr_id>', methods=['GET'])
@jwt_required
def tgs_ovr(ovr_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, TGOVR, TGOVR.ovr_id, ovr_id)


@bhadrasanaapi.route('/api/tgs', methods=['POST'])
@jwt_required
def tgs():
    return get_filtro_alchemy(TGOVR, request.json)


@bhadrasanaapi.route('/api/itemtg/<id>', methods=['GET'])
@jwt_required
def iemtg(id):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session, ItemTG, ItemTG.id, id)


@bhadrasanaapi.route('/api/itenstg', methods=['POST'])
@jwt_required
def itenstg():
    return get_filtro_alchemy(ItemTG, request.json)


@bhadrasanaapi.route('/api/itenstg/<tg_id>', methods=['GET'])
@jwt_required
def itenstg_tg(tg_id):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, ItemTG, ItemTG.tg_id, tg_id)


@bhadrasanaapi.route('/api/get_cpf_telegram/<telegram_user>')
@jwt_required
def get_cpf_telegram(telegram_user):
    """Exibe o editor Open Source JS (licença MIT) FileRobot."""
    session = current_app.config['db_session']
    user = get_usuario_telegram(session, telegram_user)
    print('********', user, telegram_user)
    if user is None:
        return jsonify({'cpf': None}), 404
    return jsonify({'cpf': user.cpf}), 200


@bhadrasanaapi.route('/api/minhas_fichas/<cpf>', methods=['GET'])
@jwt_required
def minhas_fichas_json(cpf):
    session = current_app.config['db_session']
    try:
        ovrs = get_ovr_responsavel(session, cpf)
        if len(ovrs) == 0:
            return jsonify(
                {'msg': 'Sem Fichas atribuídas para o Usuário {}'.format(cpf)}), 404
        exibicao = ExibicaoOVR(session, TipoExibicao.Descritivo, cpf)
        chaves = exibicao.get_titulos()
        result = []
        for ovr in ovrs:
            id, visualizado, linha = exibicao.get_linha(ovr)
            datahora = datetime.strftime(linha[0], '%d/%m/%Y %H:%M')
            linha_dict = {chaves[0]: id, chaves[1]: datahora}
            for key, value in zip(chaves[2:], linha[1:]):
                linha_dict[key] = value
            result.append(linha_dict)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro! Detalhes no log da aplicação.' + str(err)}), 400
    return jsonify(result), 200


@bhadrasanaapi.route('/api/consulta_conteiner', methods=['POST'])
@jwt_required
def consulta_conteiner():
    """Tela para consulta única de número de contêiner.

    Dentro do intervalo de datas, traz lista de ojetos do sistema que contenham
    alguma referência ao contêiner.
    """
    session = current_app.config['db_session']
    mongodb = current_app.config['mongodb']
    try:
        rvfs, ovrs, infoces, dues, eventos = \
            consulta_container_objects(request.json, session, mongodb)
        result = {
            'rvfs': [rvf.dump(explode=False) for rvf in rvfs],
            'ovrs': [ovr.dump(explode=False) for ovr in ovrs],
            'infoces': infoces,
            'dues': dues,
            'eventos': eventos
        }
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro! Detalhes no log da aplicação.' + str(err)}), 400
    return jsonify(result), 200


@bhadrasanaapi.route('/api/consulta_empresa', methods=['POST'])
@jwt_required
def consulta_empresa():
    """Tela para consulta única de Empresa.

    Dentro do intervalo de datas, traz lista de ojetos do sistema que contenham
    alguma referência ao CNPJ da Empresa. Permite encontrar CNPJ através do nome.
    """
    session = current_app.config['db_session']
    mongodb = current_app.config['mongodb']
    try:
        # TODO: Refactor para função e filtrar datas
        cnpj = request.json['cnpj']
        empresa = get_empresa(session, cnpj)
        dues = get_dues_empresa(mongodb,
                                cnpj)
        ovrs = get_ovr_empresa(session, cnpj)
        conhecimentos = get_ces_empresa(session, cnpj)
        listaCE = [ce.numeroCEmercante for ce in conhecimentos]
        infoces = get_detalhes_mercante(session, listaCE)
        sats = get_sats_cnpj(session, cnpj)
        result = {
            'empresa': empresa.nome if empresa else '',
            'ovrs': [ovr.dump(explode=False) for ovr in ovrs],
            'infoces': infoces,
            'dues': dues,
            'sats': [dump_model(sat) for sat in sats]
        }
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify(
            {'msg': 'Erro! Detalhes no log da aplicação.' + str(err)}), 400
    return jsonify(result), 200


if __name__ == '__main__':  # pragma: no cover
    from ajnaapi.utils import yaml_from_model

    # print(yaml_from_model(OVR))
    # print(yaml_from_model(RVF))
    # print(yaml_from_model(ImagemRVF))
    # print(yaml_from_model(EventoOVR))
    print(yaml_from_model(ItemTG))
