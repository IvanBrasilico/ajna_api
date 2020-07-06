import collections

from dateutil.parser import parse
from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, BigInteger, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

from ajnaapi.recintosapi.models import Base, EventoBase
from ajnaapi.config import Production


class AgendamentoConferencia(EventoBase):
    __tablename__ = 'recinto_agendamentos'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    dtHrAgenda = Column(DateTime)

    listaConteineresUld = relationship('ConteinerUld', back_populates='acessoveiculo')
    listaCameras = []

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        if kwargs.get('dtHrAgenda'):
            self.dtHrAgenda = parse(kwargs.get('dtHrAgenda'))

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
    pesoBrutoManifesto = Column(Numeric(6))
    placa = Column(String(7))
    # TODO: tara está duplicada???
    # tara = Column(Numeric(10))
    listaSemirreboque = relationship('Semirreboque', back_populates='pesagemveiculo')
    taraConjunto = Column(Numeric(5))
    numConteinerUld = Column(String(11))
    tipoConteinerUld = Column(String(5))
    taraConteinerUld = Column(Numeric(5))
    pesoBrutoBalanca = Column(Numeric(6))
    capturaAutoPeso = Column(Boolean)
    dutos = Column(String(1))
    volume = Column(Numeric(5, 2))
    balanca = Column(String(40))
    listaCameras = []

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.listaManifestos = []
        self.pesoBrutoManifesto = kwargs.get('pesoBrutoManifesto')
        self.placa = kwargs.get('placa')
        self.taraConjunto = kwargs.get('taraConjunto')
        self.numConteinerUld = kwargs.get('numConteinerUld')
        self.tipoConteinerUld = kwargs.get('tipoConteinerUld')
        self.taraConteinerUld = kwargs.get('taraConteinerUld')
        self.pesoBrutoBalanca = kwargs.get('pesoBrutoBalanca')
        self.capturaAutoPeso = kwargs.get('capturaAutoPeso')
        self.dutos = kwargs.get('dutos')
        self.volume = kwargs.get('volume')
        self.balanca = kwargs.get('balanca')
        self.listaCameras = []

    @validates('placa', 'numConteinerUld', 'tipoConteinerUld', 'dutos')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


if __name__ == '__main__':
    engine = Production.sql
    # Base.metadata.drop_all(engine, [])
    Base.metadata.create_all(engine)
