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


class Semirreboque(SQLAlchemyAutoSchema):
    class Meta:
        model = orm.Semirreboque
        include_fk = True
        load_instance = True


class PesagemVeiculo(SQLAlchemyAutoSchema):
    listaSemirreboque = fields.Nested('Semirreboque', many=True,
                                      exclude=('id',))

    class Meta:
        model = orm.PesagemVeiculo
        include_relationships = True
        load_instance = True
