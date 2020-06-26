from flask_jwt_extended import jwt_required

from flask import Blueprint, request

from ajnaapi.utils import select_one_from_class, select_many_from_class, \
    get_datamodificacao_gt, get_filtro
from virasana.integracao.mercante.mercantealchemy import Conhecimento, \
    ConteinerVazio, Item, Manifesto, NCMItem, Escala


mercanteapi = Blueprint('mercanteapi', __name__)


@mercanteapi.route('/api/conhecimentos/<numeroCEmercante>', methods=['GET'])
@jwt_required
def conhecimento_numero(numeroCEmercante):
    return select_one_from_class(Conhecimento,
                                 Conhecimento.numeroCEmercante,
                                 numeroCEmercante)


@mercanteapi.route('/api/conhecimentos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def conhecimento_new(datamodificacao):
    return get_datamodificacao_gt(Conhecimento, datamodificacao)


@mercanteapi.route('/api/conhecimentos', methods=['GET', 'POST'])
@jwt_required
def conhecimentos_list():
    return get_filtro(Conhecimento, request.values)


@mercanteapi.route('/api/manifestos/<numero>', methods=['GET'])
@jwt_required
def manifesto_numero(numero):
    return select_one_from_class(Manifesto,
                                 Manifesto.numero,
                                 numero)


@mercanteapi.route('/api/manifestos/new/<datamodificacao>', methods=['GET'])
@jwt_required
def manifestos_new(datamodificacao):
    return get_datamodificacao_gt(Manifesto, datamodificacao)


@mercanteapi.route('/api/manifestos', methods=['GET', 'POST'])
@jwt_required
def manifestos_list():
    return get_filtro(Manifesto, request.values)


@mercanteapi.route('/api/itens/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def itens_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro(Item, query)


@mercanteapi.route('/api/itens/new/<datamodificacao>', methods=['GET'])
@jwt_required
def itens_new(datamodificacao):
    return get_datamodificacao_gt(Item, datamodificacao)


@mercanteapi.route('/api/itens', methods=['GET', 'POST'])
@jwt_required
def itens_list():
    return get_filtro(Item, request.values)


@mercanteapi.route('/api/itens/<conhecimento>', methods=['GET'])
@jwt_required
def itens_conhecimento(conhecimento):
    return select_many_from_class(Item,
                                  Item.numeroCEmercante,
                                  conhecimento)


@mercanteapi.route('/api/NCMItem/<conhecimento>/<sequencial>', methods=['GET'])
@jwt_required
def NCMItem_numero(conhecimento, sequencial):
    query = {'numeroCEmercante': conhecimento,
             'numeroSequencialItemCarga': sequencial}
    return get_filtro(NCMItem, query)


@mercanteapi.route('/api/NCMItem/new/<datamodificacao>', methods=['GET'])
@jwt_required
def NCMItem_new(datamodificacao):
    return get_datamodificacao_gt(NCMItem, datamodificacao)


@mercanteapi.route('/api/NCMItem', methods=['GET', 'POST'])
@jwt_required
def NCMItem_list():
    return get_filtro(NCMItem, request.values)


@mercanteapi.route('/api/NCMItem/<conhecimento>', methods=['GET'])
@jwt_required
def NCMItem_conhecimento(conhecimento):
    return select_many_from_class(NCMItem,
                                  NCMItem.c.numeroCEmercante,
                                  conhecimento)


@mercanteapi.route('/api/ConteinerVazio/new/<datamodificacao>', methods=['GET'])
@jwt_required
def ConteinerVazio_new(datamodificacao):
    return get_datamodificacao_gt(ConteinerVazio, datamodificacao)


@mercanteapi.route('/api/ConteinerVazio', methods=['GET', 'POST'])
@jwt_required
def ConteinerVazio_list():
    return get_filtro(ConteinerVazio, request.values)


@mercanteapi.route('/api/ConteinerVazio/<manifesto>', methods=['GET'])
@jwt_required
def ConteinerVazio_manifesto(manifesto):
    return select_many_from_class(ConteinerVazio,
                                  ConteinerVazio.c.manifesto,
                                  manifesto)


@mercanteapi.route('/api/escalas/new/<datamodificacao>', methods=['GET'])
@jwt_required
def Escala_new(datamodificacao):
    return get_datamodificacao_gt(Escala, datamodificacao)


@mercanteapi.route('/api/escalas', methods=['GET', 'POST'])
@jwt_required
def Escala_list():
    return get_filtro(Escala, request.values)


@mercanteapi.route('/api/escalas/<numeroDaEscala>', methods=['GET'])
#@jwt_required
def Escala_manifesto(numeroDaEscala):
    return select_one_from_class(Escala,
                                 Escala.numeroDaEscala,
                                 numeroDaEscala)
