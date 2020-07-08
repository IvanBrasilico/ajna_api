from datetime import datetime
from enum import Enum

from dateutil.parser import parse
from sqlalchemy import Column, DateTime, Integer, \
    String, BigInteger, ForeignKey
from sqlalchemy.orm import validates, relationship

from ajnaapi.config import Production
from ajnaapi.recintosapi.models import Base, EventoBase, BaseDumpable


class TipoAgendamento(Enum):
    SolicitadoRFB = 1
    AgendadoRecinto = 2
    ConfirmadoRFB = 3


class AgendamentoConferencia(EventoBase):
    __tablename__ = 'recinto_agendamentos'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    dtHrAgenda = Column(DateTime)
    tipo = Column(Integer)
    listaConteineres = []
    listaCameras = []

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        if kwargs.get('dtHrAgenda'):
            self.dtHrAgenda = parse(kwargs.get('dtHrAgenda'))

    def dump(self):
        result = super().dump()
        result['dtHrAgenda'] = datetime.strftime(self.dtHrAgenda, '%Y-%m-%dT%M:%H:%S')
        return result

    @validates('nmtransportador', 'motorista_nome', 'mercadoria')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class VerificacaoFisica(EventoBase):
    __tablename__ = 'recinto_verificacoes'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    listaManifestos = []
    numConteiner = Column(String(11))
    listaCameras = []
    listaImagens = []

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.listaManifestos = []
        self.numConteiner = kwargs.get('numConteinerUld')
        self.listaCameras = []

    @validates('numConteinerUld')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class ImagemVerificacaoFisica(BaseDumpable):
    __tablename__ = 'recinto_imagensverificacao'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    camera = Column(String(20))
    verificacaofisica_id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                                  ForeignKey('recinto_verificacoes.id'))
    verificacaofisica = relationship(
        'VerificacaoFisica'
    )

    def __init__(self, verificacaofisica_id, camera, data):
        self.verificacaofisica_id = verificacaofisica_id
        self.camera = camera
        self.data = data


if __name__ == '__main__':
    engine = Production.sql
    # Base.metadata.drop_all(engine, [])
    Base.metadata.create_all(engine)
