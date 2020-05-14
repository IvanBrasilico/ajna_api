from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from ajnaapi.recintosapi import models as orm


class ConteinerUld(ModelSchema):
    class Meta:
        model = orm.ConteinerUld

class AcessoVeiculo(ModelSchema):
    listaConteineresUld = fields.Nested('ConteinerUld', many=True,
                                        exclude=('id', 'acessoveiculo'))

    class Meta:
        model = orm.AcessoVeiculo
