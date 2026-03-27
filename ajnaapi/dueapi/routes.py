'''DUE API Routes - Declaração Única de Exportação endpoints.'''

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ajna_commons.utils.sanitiza import mongo_sanitizar
from virasana.integracao.due.due_alchemy import (Due, DueItem,
                                                 DueConteiner)

dueapi = Blueprint('dueapi', __name__)


@dueapi.route('/api/due/<numero_due>', methods=['GET'])
@jwt_required()
def api_get_due(numero_due):
    """Retorna informações de uma Declaração Única de Exportação (DUE).

    Args:
        numero_due: Número da DUE (14 caracteres)

    Returns:
        JSON com dados da DUE ou erro 404
    """
    db_session = current_app.config['db_session']
    numero_due = mongo_sanitizar(numero_due)

    try:
        due = db_session.query(Due).filter(Due.numero_due == numero_due).first()

        if not due:
            return jsonify({'msg': f'DUE {numero_due} não encontrada'}), 404

        due_dict = {
            'numero_due': due.numero_due,
            'data_criacao_due': due.data_criacao_due.isoformat()
            if due.data_criacao_due else None,
            'data_registro_due': due.data_registro_due.isoformat()
            if due.data_registro_due else None,
            'ni_declarante': due.ni_declarante,
            'cnpj_estabelecimento_exportador': due.cnpj_estabelecimento_exportador,
            'telefone_contato': due.telefone_contato,
            'email_contato': due.email_contato,
            'nome_contato': due.nome_contato,
            'codigo_iso3_pais_importador': due.codigo_iso3_pais_importador,
            'nome_pais_importador': due.nome_pais_importador,
            'duev_nm_tp_doc_fiscal_c': due.duev_nm_tp_doc_fiscal_c,
            'duev_cetp_nm_c': due.duev_cetp_nm_c,
            'codigo_recinto_despacho': due.codigo_recinto_despacho,
            'codigo_recinto_embarque': due.codigo_recinto_embarque,
            'codigo_unidade_embarque': due.codigo_unidade_embarque,
            'conteiners': due.get_lista_conteiners()
            if due.lista_id_conteiner else [],
        }

        return jsonify(due_dict), 200

    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao buscar DUE: {str(err)}'}), 400


@dueapi.route('/api/dues', methods=['GET', 'POST'])
@jwt_required()
def api_dues():
    """Lista DUEs ou cria/atualiza uma DUE.

    GET: Retorna lista de DUEs conforme filtro
    POST: Insere/atualiza uma DUE
    """
    db_session = current_app.config['db_session']

    try:
        if request.method == 'POST':
            data = request.get_json()

            numero_due = data.get('numero_due')
            if not numero_due:
                return jsonify({'msg': 'numero_due é obrigatório'}), 400

            due = db_session.query(Due).filter(Due.numero_due == numero_due).first()

            if due:
                # Atualizar DUE existente
                due.ni_declarante = data.get('ni_declarante', due.ni_declarante)
                due.cnpj_estabelecimento_exportador = data.get('cnpj_estabelecimento_exportador',
                                                               due.cnpj_estabelecimento_exportador)
                due.telefone_contato = data.get('telefone_contato', due.telefone_contato)
                due.email_contato = data.get('email_contato', due.email_contato)
                due.nome_contato = data.get('nome_contato', due.nome_contato)
                message = 'DUE atualizada com sucesso'
            else:
                # Criar nova DUE
                due = Due(
                    numero_due=numero_due,
                    ni_declarante=data.get('ni_declarante'),
                    cnpj_estabelecimento_exportador=data.get('cnpj_estabelecimento_exportador'),
                    telefone_contato=data.get('telefone_contato'),
                    email_contato=data.get('email_contato'),
                    nome_contato=data.get('nome_contato'),
                    codigo_iso3_pais_importador=data.get('codigo_iso3_pais_importador'),
                    nome_pais_importador=data.get('nome_pais_importador'),
                    duev_nm_tp_doc_fiscal_c=data.get('duev_nm_tp_doc_fiscal_c'),
                    duev_cetp_nm_c=data.get('duev_cetp_nm_c'),
                    codigo_recinto_despacho=data.get('codigo_recinto_despacho'),
                    codigo_recinto_embarque=data.get('codigo_recinto_embarque'),
                    codigo_unidade_embarque=data.get('codigo_unidade_embarque'),
                    lista_id_conteiner=data.get('lista_id_conteiner', ''),
                )
                db_session.add(due)
                message = 'DUE criada com sucesso'

            db_session.commit()
            current_app.logger.info(f'{message}: {numero_due}')
            return jsonify({'msg': message, 'numero_due': numero_due}), 201

        else:
            # GET - Listar DUEs

            filtro = {mongo_sanitizar(key): mongo_sanitizar(value)
                      for key, value in request.args.items()}
            query = db_session.query(Due)
            if 'ni_declarante' in filtro:
                query = query.filter(Due.ni_declarante == filtro['ni_declarante'])
            if 'cnpj_estabelecimento_exportador' in filtro:
                query = query.filter(Due.cnpj_estabelecimento_exportador ==
                                     filtro['cnpj_estabelecimento_exportador'])

            dues = query.limit(1000).all()

            if not dues:
                return jsonify({}), 404

            dues_list = [{
                'numero_due': due.numero_due,
                'data_criacao_due': due.data_criacao_due.isoformat() if due.data_criacao_due else None,
                'ni_declarante': due.ni_declarante,
                'cnpj_estabelecimento_exportador': due.cnpj_estabelecimento_exportador,
                'nome_pais_importador': due.nome_pais_importador,
            } for due in dues]

            return jsonify(dues_list), 200

    except IntegrityError as err:
        db_session.rollback()
        current_app.logger.error(f'Erro de integridade: {err}', exc_info=True)
        return jsonify({'msg': 'Número de DUE já existe'}), 409
    except SQLAlchemyError as err:
        db_session.rollback()
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao processar DUE: {str(err)}'}), 400
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro inesperado: {str(err)}'}), 400


@dueapi.route('/api/due/<numero_due>/itens', methods=['GET'])
@jwt_required()
def api_due_itens(numero_due):
    """Retorna os itens de uma Declaração Única de Exportação (DUE).

    Args:
        numero_due: Número da DUE (14 caracteres)

    Returns:
        JSON com lista de itens da DUE
    """
    db_session = current_app.config['db_session']
    numero_due = mongo_sanitizar(numero_due)

    try:
        itens = db_session.query(DueItem).filter(DueItem.nr_due == numero_due).all()

        if not itens:
            return jsonify({}), 404

        itens_list = [{
            'nr_due': item.nr_due,
            'due_nr_item': item.due_nr_item,
            'descricao_item': item.descricao_item,
            'descricao_complementar_item': item.descricao_complementar_item,
            'nfe_nr_item': item.nfe_nr_item,
            'nfe_ncm': item.nfe_ncm,
            'unidade_comercial': item.unidade_comercial,
            'qt_unidade_comercial': float(item.qt_unidade_comercial) if item.qt_unidade_comercial else None,
            'valor_total_due_itens': float(item.valor_total_due_itens) if item.valor_total_due_itens else None,
            'nfe_nm_importador': item.nfe_nm_importador,
            'pais_destino_item': item.pais_destino_item,
        } for item in itens]

        return jsonify(itens_list), 200

    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao buscar itens da DUE: {str(err)}'}), 400


@dueapi.route('/api/due/<numero_due>/conteiners', methods=['GET'])
@jwt_required()
def api_due_conteiners(numero_due):
    """Retorna os contêineres associados a uma Declaração Única de Exportação (DUE).

    Args:
        numero_due: Número da DUE (14 caracteres)

    Returns:
        JSON com lista de contêineres da DUE
    """
    db_session = current_app.config['db_session']
    numero_due = mongo_sanitizar(numero_due)

    try:
        # Verificar se DUE existe
        due = db_session.query(Due).filter(Due.numero_due == numero_due).first()
        if not due:
            return jsonify({'msg': f'DUE {numero_due} não encontrada'}), 404

        # Buscar contêineres
        conteiners = db_session.query(DueConteiner).filter(
            DueConteiner.numero_due == numero_due
        ).all()

        if not conteiners:
            return jsonify({}), 404

        conteiners_list = [{
            'id': conteiner.id,
            'numero_due': conteiner.numero_due,
            'numero_conteiner': conteiner.numero_conteiner,
        } for conteiner in conteiners]

        return jsonify(conteiners_list), 200

    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao buscar contêineres da DUE: {str(err)}'}), 400


@dueapi.route('/api/conteiner/<numero_conteiner>/due', methods=['GET'])
@jwt_required()
def api_conteiner_due(numero_conteiner):
    """Retorna a DUE associada a um contêiner.

    Args:
        numero_conteiner: Número do contêiner (11 caracteres)

    Returns:
        JSON com dados da DUE associada ao contêiner
    """
    db_session = current_app.config['db_session']
    numero_conteiner = mongo_sanitizar(numero_conteiner)

    try:
        due_conteiner = db_session.query(DueConteiner).filter(
            DueConteiner.numero_conteiner == numero_conteiner
        ).first()

        if not due_conteiner:
            return jsonify({'msg': f'Contêiner {numero_conteiner} não associado a nenhuma DUE'}), 404

        due = db_session.query(Due).filter(
            Due.numero_due == due_conteiner.numero_due
        ).first()

        if not due:
            return jsonify({'msg': 'DUE associada não encontrada'}), 404

        due_dict = {
            'numero_due': due.numero_due,
            'data_criacao_due': due.data_criacao_due.isoformat() if due.data_criacao_due else None,
            'ni_declarante': due.ni_declarante,
            'cnpj_estabelecimento_exportador': due.cnpj_estabelecimento_exportador,
            'nome_pais_importador': due.nome_pais_importador,
            'conteiners': due.get_lista_conteiners() if due.lista_id_conteiner else [],
        }

        return jsonify(due_dict), 200

    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao buscar DUE do contêiner: {str(err)}'}), 400
