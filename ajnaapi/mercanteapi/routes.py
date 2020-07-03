from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required

from ajnaapi.utils import select_one_campo_alchemy, get_filtro_alchemy, \
    get_datamodificacao_gt_alchemy, select_many_campo_alchemy
from virasana.integracao.mercante.mercantealchemy import Conhecimento, \
    ConteinerVazio, Item, Manifesto, NCMItem, Escala

mercanteapi = Blueprint('mercanteapi', __name__)


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
@jwt_required
def conhecimento_numero(numeroCEmercante):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session,
                                    Conhecimento,
                                    Conhecimento.numeroCEmercante,
                                    numeroCEmercante)


@mercanteapi.route('/api/conhecimentos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def conhecimento_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(Conhecimento, datamodificacao)


@mercanteapi.route('/api/conhecimentos', methods=['GET', 'POST'])
@jwt_required
def conhecimentos_list():
    return get_filtro_alchemy(Conhecimento, request.values)


@mercanteapi.route('/api/manifestos/<numero>', methods=['GET'])
@jwt_required
def manifesto_numero(numero):
    session = current_app.config['db_session']
    return select_one_campo_alchemy(session,
                                    Manifesto,
                                    Manifesto.numero,
                                    numero)


@mercanteapi.route('/api/manifestos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def manifestos_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(Manifesto, datamodificacao)


@mercanteapi.route('/api/manifestos', methods=['GET', 'POST'])
@jwt_required
def manifestos_list():
    return get_filtro_alchemy(Manifesto, request.values)


@mercanteapi.route('/api/item/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def itens_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro_alchemy(Item, query)


@mercanteapi.route('/api/itens/new/<datamodificacao>', methods=['GET'])
@jwt_required
def itens_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(Item, datamodificacao)


@mercanteapi.route('/api/itens', methods=['GET', 'POST'])
@jwt_required
def itens_list():
    return get_filtro_alchemy(Item, request.values)


@mercanteapi.route('/api/itens/<conhecimento>', methods=['GET'])
@jwt_required
def itens_conhecimento(conhecimento):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, Item,
                                     Item.numeroCEmercante,
                                     conhecimento)


@mercanteapi.route('/api/NCMItem/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def NCMItem_numero(conhecimento, sequencial):
    # TODO: Refactor NCMItem de numeroCEMercante para numeroCEmercante
    # Atenção!!! Problema original é no XML de entrada!!!!
    query = {'numeroCEMercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro_alchemy(NCMItem, query)


@mercanteapi.route('/api/NCMItem/new/<datamodificacao>', methods=['GET'])
@jwt_required
def NCMItem_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(NCMItem, datamodificacao)


@mercanteapi.route('/api/NCMItem', methods=['GET', 'POST'])
@jwt_required
def NCMItem_list():
    return get_filtro_alchemy(NCMItem, request.values)


@mercanteapi.route('/api/NCMItem/<conhecimento>', methods=['GET'])
@jwt_required
def NCMItem_conhecimento(conhecimento):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, NCMItem,
                                     NCMItem.numeroCEMercante,
                                     conhecimento)


@mercanteapi.route('/api/ConteinerVazio/new/<datamodificacao>', methods=['GET'])
@jwt_required
def ConteinerVazio_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(ConteinerVazio, datamodificacao)


@mercanteapi.route('/api/ConteinerVazio', methods=['GET', 'POST'])
@jwt_required
def ConteinerVazio_list():
    return get_filtro_alchemy(ConteinerVazio, request.values)


@mercanteapi.route('/api/ConteinerVazio/<manifesto>', methods=['GET'])
@jwt_required
def ConteinerVazio_manifesto(manifesto):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, ConteinerVazio,
                                     ConteinerVazio.manifesto,
                                     manifesto)


@mercanteapi.route('/api/escalas/new/<datamodificacao>', methods=['GET'])
@jwt_required
def Escala_new(datamodificacao):
    return get_datamodificacao_gt_alchemy(Escala, datamodificacao)


@mercanteapi.route('/api/escalas', methods=['GET', 'POST'])
@jwt_required
def Escala_list():
    return get_filtro_alchemy(Escala, request.values)


@mercanteapi.route('/api/escalas/<numeroDaEscala>', methods=['GET'])
@jwt_required
def Escala_manifesto(numeroDaEscala):
    session = current_app.config['db_session']
    return select_many_campo_alchemy(session, Escala,
                                     Escala.numeroDaEscala,
                                     numeroDaEscala)
