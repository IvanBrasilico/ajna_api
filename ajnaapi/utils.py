from dateutil import parser
from flask import current_app, jsonify
from ruamel import yaml
from sqlalchemy import select, and_
from sqlalchemy.engine import RowProxy
from sqlalchemy.orm.attributes import InstrumentedAttribute


def exclude_from_dict(dict, exclude:list = None):
    if exclude:
        for key in exclude:
            if dict.get(key):
                dict.pop(key)

def dump_rowproxy(rowproxy: RowProxy, exclude: list = None):
    dump = dict([(k, v) for k, v in rowproxy.items() if not k.startswith('_')])
    return exclude(dump, exclude)

def dump_model(model, exclude: list = None):
    dump = dict([(k, v) for k, v in vars(model).items() if not k.startswith('_')])
    return exclude(dump, exclude)

def select_one_from_class(table, campo, valor):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                campo == valor)
            result = conn.execute(s).fetchone()
        if result:
            return jsonify(dump_rowproxy(result)), 200
        else:
            return jsonify({'msg': '%s Não encontrado' % table}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def select_many_from_class(table, campo, valor):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                campo == valor)
            print(campo, valor)
            result = conn.execute(s)
            if result:
                resultados = [dump_rowproxy(row) for row in result]
                if resultados and len(resultados) > 0:
                    return jsonify(resultados), 200
            return jsonify({'msg': '%s Não encontrado' % table.name}), 404
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def return_many_from_resultproxy(result):
    resultados = None
    if result:
        resultados = [dump_rowproxy(row) for row in result]
    if resultados and len(resultados) > 0:
        print(len(resultados))
        return jsonify(resultados), 200
    else:
        return jsonify({'msg': 'Não encontrado'}), 404


def get_datamodificacao_gt(table, datamodificacao):
    engine = current_app.config['sql']
    try:
        datamodificacao = parser.parse(datamodificacao)
        print(datamodificacao)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro no parâmetro: %s' % str(err)}), 400
    try:
        with engine.begin() as conn:
            s = select([table]).where(
                table.c.last_modified >= datamodificacao)
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


def get_filtro(table, uri_query):
    engine = current_app.config['sql']
    try:
        with engine.begin() as conn:
            lista_condicoes = [table.c[campo] == valor
                               for campo, valor in uri_query.items()]
            s = select([table]).where(and_(*lista_condicoes))
            result = conn.execute(s)
            return return_many_from_resultproxy(result)
    except Exception as err:
        current_app.logger.error(err, exc_info=True)
        return jsonify({'msg': 'Erro inesperado: %s' % str(err)}), 400


TYPES = {
    'str': {'type': 'string'},
    'datetime': {'type': 'string'},
    'bool': {'type': 'boolean'},
    'int': {'type': 'integer'},
    'Decimal': {'type': 'number'}
}


def yaml_from_model(model):
    yaml_dict = {}
    for c in dir(model):
        if not c.startswith('_'):
            attr = getattr(model, c)
            if isinstance(attr, InstrumentedAttribute):
                try:
                    yaml_dict[c] = dict(TYPES[attr.type.python_type.__name__])
                except (AttributeError, NotImplementedError):
                    yaml_dict[c] = {'type': 'object', 'properties': c}
                    pass
    # print(yaml_dict)
    return yaml.dump({model.__name__: yaml_dict},
                     default_flow_style=False)