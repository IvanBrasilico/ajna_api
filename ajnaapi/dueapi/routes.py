'''DUE API Routes - Declaração Única de Exportação endpoints.'''

from decimal import Decimal, InvalidOperation

from flask import Blueprint
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ajna_commons.utils.sanitiza import mongo_sanitizar
from virasana.integracao.due.due_alchemy import (Due, DueItem,
                                                 DueConteiner)

dueapi = Blueprint('dueapi', __name__)

MAX_BULK_DUES = 500


def _to_decimal(value, field_name):
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f'Campo "{field_name}" inválido para valor numérico')


def _apply_due_data(due, data, is_new=False):
    if is_new:
        due.numero_due = data.get('numero_due')

    due.ni_declarante = data.get('ni_declarante', due.ni_declarante)
    due.cnpj_estabelecimento_exportador = data.get(
        'cnpj_estabelecimento_exportador',
        due.cnpj_estabelecimento_exportador
    )
    due.telefone_contato = data.get('telefone_contato', due.telefone_contato)
    due.email_contato = data.get('email_contato', due.email_contato)
    due.nome_contato = data.get('nome_contato', due.nome_contato)
    due.codigo_iso3_pais_importador = data.get(
        'codigo_iso3_pais_importador',
        due.codigo_iso3_pais_importador
    )
    due.nome_pais_importador = data.get(
        'nome_pais_importador',
        due.nome_pais_importador
    )
    due.duev_nm_tp_doc_fiscal_c = data.get(
        'duev_nm_tp_doc_fiscal_c',
        due.duev_nm_tp_doc_fiscal_c
    )
    due.duev_cetp_nm_c = data.get('duev_cetp_nm_c', due.duev_cetp_nm_c)
    due.codigo_recinto_despacho = data.get(
        'codigo_recinto_despacho',
        due.codigo_recinto_despacho
    )
    due.codigo_recinto_embarque = data.get(
        'codigo_recinto_embarque',
        due.codigo_recinto_embarque
    )
    due.codigo_unidade_embarque = data.get(
        'codigo_unidade_embarque',
        due.codigo_unidade_embarque
    )
    due.lista_id_conteiner = data.get(
        'lista_id_conteiner',
        due.lista_id_conteiner if due.lista_id_conteiner is not None else ''
    )


def _apply_due_item_data(item, item_data, numero_due, is_new=False):
    if is_new:
        item.nr_due = numero_due
        item.due_nr_item = item_data.get('due_nr_item')

    item.descricao_item = item_data.get('descricao_item', item.descricao_item)
    item.descricao_complementar_item = item_data.get(
        'descricao_complementar_item',
        item.descricao_complementar_item
    )
    item.nfe_nr_item = item_data.get('nfe_nr_item', item.nfe_nr_item)
    item.nfe_ncm = item_data.get('nfe_ncm', item.nfe_ncm)
    item.unidade_comercial = item_data.get('unidade_comercial', item.unidade_comercial)
    item.qt_unidade_comercial = (
        _to_decimal(item_data['qt_unidade_comercial'], 'qt_unidade_comercial')
        if 'qt_unidade_comercial' in item_data
        else item.qt_unidade_comercial
    )
    item.valor_total_due_itens = (
        _to_decimal(item_data['valor_total_due_itens'], 'valor_total_due_itens')
        if 'valor_total_due_itens' in item_data
        else item.valor_total_due_itens
    )
    item.nfe_nm_importador = item_data.get('nfe_nm_importador', item.nfe_nm_importador)
    item.pais_destino_item = item_data.get('pais_destino_item', item.pais_destino_item)


def _sync_due_items(due, itens_payload):
    if itens_payload is None:
        return {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }

    if not isinstance(itens_payload, list):
        raise ValueError('Campo "itens" deve ser uma lista')

    existing_items = {item.due_nr_item: item for item in due.itens}
    payload_keys = set()

    created = 0
    updated = 0

    for item_data in itens_payload:
        if not isinstance(item_data, dict):
            raise ValueError('Cada item de "itens" deve ser um objeto JSON')

        due_nr_item = item_data.get('due_nr_item')
        if due_nr_item is None:
            raise ValueError('Campo "due_nr_item" é obrigatório em cada item')

        if due_nr_item in payload_keys:
            raise ValueError(f'due_nr_item duplicado no payload: {due_nr_item}')

        payload_keys.add(due_nr_item)

        existing = existing_items.get(due_nr_item)
        if existing:
            _apply_due_item_data(existing, item_data, due.numero_due, is_new=False)
            updated += 1
        else:
            new_item = DueItem()
            _apply_due_item_data(new_item, item_data, due.numero_due, is_new=True)
            due.itens.append(new_item)
            created += 1

    deleted = 0
    for due_nr_item, existing in list(existing_items.items()):
        if due_nr_item not in payload_keys:
            due.itens.remove(existing)
            deleted += 1

    return {
        'created': created,
        'updated': updated,
        'deleted': deleted
    }


@dueapi.route('/api/dues/bulk', methods=['POST'])
@jwt_required()
def api_dues_bulk():
    """
    Processa várias DUEs em lote com itens.

    Payload:
    {
      "items": [
        {
          "numero_due": "12345678901234",
          "ni_declarante": "12345678901234",
          "itens": [
            {
              "due_nr_item": 1,
              "descricao_item": "PRODUTO A",
              "qt_unidade_comercial": 10,
              "valor_total_due_itens": 1500.55
            }
          ]
        }
      ]
    }
    """
    db_session = current_app.config['db_session']

    try:
        payload = request.get_json() or {}
        items = payload.get('items')

        if not isinstance(items, list):
            return jsonify({'msg': 'Payload deve conter "items" como lista'}), 400

        if not items:
            return jsonify({'msg': 'Lista "items" vazia'}), 400

        if len(items) > MAX_BULK_DUES:
            return jsonify({
                'msg': f'Lote excede o limite máximo de {MAX_BULK_DUES} DUEs por requisição'
            }), 413

        results = []
        created = 0
        updated = 0
        failed = 0

        for idx, data in enumerate(items):
            savepoint = db_session.begin_nested()
            try:
                if not isinstance(data, dict):
                    raise ValueError('Cada item deve ser um objeto JSON')

                numero_due = data.get('numero_due')
                if not numero_due:
                    raise ValueError('numero_due é obrigatório')

                due = db_session.query(Due).filter(Due.numero_due == numero_due).first()

                if due:
                    _apply_due_data(due, data, is_new=False)
                    due_operation = 'updated'
                    updated += 1
                else:
                    due = Due()
                    _apply_due_data(due, data, is_new=True)
                    db_session.add(due)
                    due_operation = 'created'
                    created += 1

                item_summary = _sync_due_items(due, data.get('itens'))
                db_session.flush()
                savepoint.commit()

                results.append({
                    'index': idx,
                    'numero_due': numero_due,
                    'status': 'success',
                    'operation': due_operation,
                    'itens': item_summary
                })

            except IntegrityError as err:
                savepoint.rollback()
                failed += 1
                current_app.logger.error(
                    f'Erro de integridade no item {idx}: {err}',
                    exc_info=True
                )
                results.append({
                    'index': idx,
                    'numero_due': data.get('numero_due') if isinstance(data, dict) else None,
                    'status': 'error',
                    'error_type': 'integrity_error',
                    'msg': 'Erro de integridade ao processar a DUE'
                })

            except (SQLAlchemyError, ValueError) as err:
                savepoint.rollback()
                failed += 1
                current_app.logger.error(
                    f'Erro no item {idx}: {err}',
                    exc_info=True
                )
                results.append({
                    'index': idx,
                    'numero_due': data.get('numero_due') if isinstance(data, dict) else None,
                    'status': 'error',
                    'error_type': 'processing_error',
                    'msg': str(err)
                })

            except Exception as err:
                savepoint.rollback()
                failed += 1
                current_app.logger.error(
                    f'Erro inesperado no item {idx}: {err}',
                    exc_info=True
                )
                results.append({
                    'index': idx,
                    'numero_due': data.get('numero_due') if isinstance(data, dict) else None,
                    'status': 'error',
                    'error_type': 'unexpected_error',
                    'msg': 'Erro inesperado ao processar item'
                })

        db_session.commit()

        response = {
            'summary': {
                'total': len(items),
                'created': created,
                'updated': updated,
                'failed': failed
            },
            'results': results
        }

        if failed == 0:
            return jsonify(response), 201
        if created > 0 or updated > 0:
            return jsonify(response), 207

        return jsonify(response), 400

    except SQLAlchemyError as err:
        db_session.rollback()
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro de banco ao processar lote de DUEs'}), 400

    except Exception as err:
        db_session.rollback()
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro inesperado: {str(err)}'}), 400


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

            try:
                db_session.commit()
                current_app.logger.info(f'{message}: {numero_due}')
                return jsonify({'msg': message, 'numero_due': numero_due}), 201
            except Exception as err:
                db_session.rollback()
                raise err


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
        current_app.logger.error(f'Erro de integridade: {err}', exc_info=True)
        return jsonify({'msg': 'Número de DUE já existe'}), 409
    except SQLAlchemyError as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao processar DUE: {str(err)}'}), 400
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro inesperado: {str(err)}'}), 400


@dueapi.route('/api/due/<numero_due>/itens', methods=['GET'])
@jwt_required()
def api_due_itens_get(numero_due):
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


@dueapi.route('/api/due-itens', methods=['GET', 'POST'])
@jwt_required()
def api_due_itens():
    """Lista itens de DUE ou cria/atualiza um item de DUE.

    GET: Retorna lista de itens conforme filtro
    POST: Insere/atualiza um item de DUE
    """
    db_session = current_app.config['db_session']

    try:
        if request.method == 'POST':
            data = request.get_json() or {}

            nr_due = data.get('nr_due')
            due_nr_item = data.get('due_nr_item')

            if not nr_due:
                return jsonify({'msg': 'nr_due é obrigatório'}), 400

            if due_nr_item is None:
                return jsonify({'msg': 'due_nr_item é obrigatório'}), 400

            due_item = (
                db_session.query(DueItem)
                .filter(DueItem.nr_due == nr_due,
                        DueItem.due_nr_item == due_nr_item)
                .first()
            )

            if due_item:
                # Atualizar item existente
                due_item.descricao_item = data.get(
                    'descricao_item',
                    due_item.descricao_item
                )
                due_item.descricao_complementar_item = data.get(
                    'descricao_complementar_item',
                    due_item.descricao_complementar_item
                )
                due_item.nfe_nr_item = data.get(
                    'nfe_nr_item',
                    due_item.nfe_nr_item
                )
                due_item.nfe_ncm = data.get(
                    'nfe_ncm',
                    due_item.nfe_ncm
                )
                due_item.unidade_comercial = data.get(
                    'unidade_comercial',
                    due_item.unidade_comercial
                )
                due_item.qt_unidade_comercial = data.get(
                    'qt_unidade_comercial',
                    due_item.qt_unidade_comercial
                )
                due_item.valor_total_due_itens = data.get(
                    'valor_total_due_itens',
                    due_item.valor_total_due_itens
                )
                due_item.nfe_nm_importador = data.get(
                    'nfe_nm_importador',
                    due_item.nfe_nm_importador
                )
                due_item.pais_destino_item = data.get(
                    'pais_destino_item',
                    due_item.pais_destino_item
                )
                message = 'Item de DUE atualizado com sucesso'
                status_code = 200
            else:
                # Criar novo item
                due_item = DueItem(
                    nr_due=nr_due,
                    due_nr_item=due_nr_item,
                    descricao_item=data.get('descricao_item'),
                    descricao_complementar_item=data.get('descricao_complementar_item'),
                    nfe_nr_item=data.get('nfe_nr_item'),
                    nfe_ncm=data.get('nfe_ncm'),
                    unidade_comercial=data.get('unidade_comercial'),
                    qt_unidade_comercial=data.get('qt_unidade_comercial'),
                    valor_total_due_itens=data.get('valor_total_due_itens'),
                    nfe_nm_importador=data.get('nfe_nm_importador'),
                    pais_destino_item=data.get('pais_destino_item'),
                )
                db_session.add(due_item)
                message = 'Item de DUE criado com sucesso'
                status_code = 201

            try:
                db_session.commit()
                current_app.logger.info(f'{message}: nr_due={nr_due}, due_nr_item={due_nr_item}')
                return jsonify({
                    'msg': message,
                    'nr_due': nr_due,
                    'due_nr_item': due_nr_item
                }), status_code
            except Exception as err:
                db_session.rollback()
                raise err

        else:
            # GET - Listar itens de DUE

            filtro = {
                mongo_sanitizar(key): mongo_sanitizar(value)
                for key, value in request.args.items()
            }

            query = db_session.query(DueItem)

            if 'nr_due' in filtro:
                query = query.filter(DueItem.nr_due == filtro['nr_due'])

            if 'due_nr_item' in filtro:
                query = query.filter(DueItem.due_nr_item == filtro['due_nr_item'])

            if 'nfe_ncm' in filtro:
                query = query.filter(DueItem.nfe_ncm == filtro['nfe_ncm'])

            if 'pais_destino_item' in filtro:
                query = query.filter(DueItem.pais_destino_item == filtro['pais_destino_item'])

            itens = query.limit(1000).all()

            if not itens:
                return jsonify({}), 404

            itens_list = [{
                'nr_due': item.nr_due,
                'due_nr_item': item.due_nr_item,
                'descricao_item': item.descricao_item,
                'nfe_nr_item': item.nfe_nr_item,
                'nfe_ncm': item.nfe_ncm,
                'unidade_comercial': item.unidade_comercial,
                'qt_unidade_comercial': float(item.qt_unidade_comercial)
                if item.qt_unidade_comercial is not None else None,
                'valor_total_due_itens': float(item.valor_total_due_itens)
                if item.valor_total_due_itens is not None else None,
                'nfe_nm_importador': item.nfe_nm_importador,
                'pais_destino_item': item.pais_destino_item,
            } for item in itens]

            return jsonify(itens_list), 200

    except IntegrityError as err:
        current_app.logger.error(f'Erro de integridade: {err}', exc_info=True)
        return jsonify({'msg': 'Erro de integridade ao processar item de DUE'}), 409

    except SQLAlchemyError as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro ao processar item de DUE: {str(err)}'}), 400

    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': f'Erro inesperado: {str(err)}'}), 400
