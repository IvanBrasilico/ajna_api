from ruamel import yaml
from sqlalchemy.orm.attributes import InstrumentedAttribute

from ajnaapi.recintosapi import models

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


if __name__ == '__main__':
    # print(yaml_from_model(models.AcessoVeiculo))
    # print(yaml_from_model(models.ConteinerUld))
    print(yaml_from_model(models.PesagemVeiculo))
    print(yaml_from_model(models.Semirreboque))
