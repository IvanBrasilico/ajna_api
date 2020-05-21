from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ajnaapi.recintosapi import models as orm


class ConteinerUld(SQLAlchemyAutoSchema):
    class Meta:
        model = orm.ConteinerUld
        include_fk = True
        load_instance = True


class AcessoVeiculo(SQLAlchemyAutoSchema):
    listaConteineresUld = fields.Nested('ConteinerUld', many=True,
                                        exclude=('id',))

    class Meta:
        model = orm.AcessoVeiculo
        include_relationships = True
        load_instance = True
