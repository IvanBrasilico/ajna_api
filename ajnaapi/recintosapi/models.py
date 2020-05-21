import collections

from dateutil.parser import parse
from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, BigInteger, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

from ajnaapi.config import Production

Base = declarative_base()
db_session = None
engine = None


class BaseDumpable(Base):
    __abstract__ = True

    def dump(self, exclude=None):
        dump = dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])
        if exclude:
            for key in exclude:
                if dump.get(key):
                    dump.pop(key)
        return dump

    def __hash__(self):
        dump = self.dump()
        clean_dump = {}
        for k, v in dump.items():
            if isinstance(v, collections.Hashable):
                clean_dump[k] = v
        _sorted = sorted([(k, v) for k, v in clean_dump.items()])
        # print('Sorted dump:', _sorted)
        ovalues = tuple([s[1] for s in _sorted])
        # print('Sorted ovalues:', ovalues)
        ohash = hash(ovalues)
        # print(ohash)
        return ohash


class EventoBase(BaseDumpable):
    __abstract__ = True
    idEvento = Column(String(20), index=True)
    dtHrOcorrencia = Column(DateTime(), index=True)
    cpfOperOcor = Column(String(14), index=True)
    dtHrRegistro = Column(DateTime(), index=True)
    cpfOperReg = Column(String(14), index=True)
    protocoloEventoRetifCanc = Column(String(40), index=True)
    contingencia = Column(Boolean())
    recinto = Column(String(10), index=True)

    def __init__(self, idEvento, dtHrOcorrencia, cpfOperOcor, dtHrRegistro,
                 cpfOperReg, protocoloEventoRetifCanc, contingencia, recinto):
        self.idEvento = idEvento
        self.dtHrOcorrencia = parse(dtHrOcorrencia)
        self.cpfOperOcor = cpfOperOcor
        self.dtHrRegistro = parse(dtHrRegistro)
        self.cpfOperReg = cpfOperReg
        self.protocoloEventoRetifCanc = protocoloEventoRetifCanc
        self.contingencia = contingencia
        self.recinto = recinto

    def dump(self):
        dump = dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])
        # dump.pop('ID')
        return dump

    def __hash__(self):
        dump = self.dump()
        clean_dump = {}
        for k, v in dump.items():
            if isinstance(v, collections.Hashable):
                clean_dump[k] = v
        _sorted = sorted([(k, v) for k, v in clean_dump.items()])
        # print('Sorted dump:', _sorted)
        ovalues = tuple([s[1] for s in _sorted])
        # print('Sorted ovalues:', ovalues)
        ohash = hash(ovalues)
        # print(ohash)
        return ohash


class AcessoVeiculo(EventoBase):
    __tablename__ = 'acessosveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    operacao = Column(String(1))
    direcao = Column(String(1))
    protocoloAgenda = Column(String(20))
    dtHrAgenda = Column(DateTime)
    listaManifestos = []
    listaDiDue = []
    listaNfe = []
    listaMalas = []
    tipoGranel = Column(String(1))
    listaChassi = []
    placa = Column(String(7))
    ocrPlaca = Column(Boolean)
    oogDimensao = Column(Boolean)
    oogPeso = Column(Boolean)
    listaSemirreboque = []
    listaConteineresUld = relationship('ConteinerUld', back_populates='acessoveiculo')
    cnpjTransportador = Column(String(14))  # TODO: cpfcnpjtransportador ????
    nmtransportador = Column(String(100))
    # TODO: Precisa mesmo desta campo protocolo????
    #  E motorista, precisa ser separado mesmo???
    motorista_protocoloCredenciamento = Column(String(40))
    motorista_cpf = Column(String(11))
    motorista_nome = Column(String(100))
    codRecintoDestino = Column(Integer())  # TODO: Não deveria ser string???
    modal = Column(String(1))
    gate = Column(String(10))
    listaCameras = []
    # TODO: Campos abaixo provisórios para o COV
    login = Column(String(40))
    mercadoria = Column(String(200))

    # TODO: dataliberacao = Column(DateTime)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.operacao = kwargs.get('operacao')
        self.direcao = kwargs.get('direcao')
        if kwargs.get('dtHrAgenda'):
            self.dtHrAgenda = parse(kwargs.get('dtHrAgenda'))
        self.listaManifestos = []
        self.listaDiDue = []
        self.listaNfe = []
        self.listaMalas = []
        self.tipoGranel = kwargs.get('tipoGranel')
        self.listaChassi = []
        self.placa = kwargs.get('placa')
        self.ocrPlaca = kwargs.get('ocrPlaca')
        self.oogDimensao = kwargs.get('oogDimensao')
        self.oogPeso = kwargs.get('oogPeso')
        self.listaSemirreboque = []
        self.cnpjTransportador = kwargs.get('cnpjTransportador')
        self.nmtransportador = kwargs.get('nmtransportador')
        if kwargs.get('motorista'):
            self.motorista_protocoloCredenciamento = \
                kwargs.get('motorista').get('protocoloCredenciamento')
            self.motorista_cpf = \
                kwargs.get('motorista').get('cpf')
            self.motorista_nome = \
                kwargs.get('motorista').get('nome')
        if kwargs.get('motorista_cpf'):
            if isinstance(kwargs.get('motorista_cpf'), str):
                self.motorista_cpf = kwargs.get('motorista_cpf')[:11]
            else:
                self.motorista_cpf = str(kwargs.get('motorista_cpf'))[:11]
        if kwargs.get('motorista_nome'):
            self.motorista_nome = kwargs.get('motorista_nome')[:100]
        self.codRecintoDestino = int(kwargs.get('codRecintoDestino'))
        self.modal = kwargs.get('modal')
        self.gate = kwargs.get('gate')
        self.listaCameras = []
        self.login = kwargs.get('login')
        self.mercadoria = kwargs.get('mercadoria')

    @validates('nmtransportador', 'motorista_nome', 'mercadoria')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class PesagemVeiculo(EventoBase):
    __tablename__ = 'pesagensveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    listaManifestos = []
    pesoBrutoManifesto = Column(Numeric(6))
    placa = Column(String(7))
    # TODO: tara está duplicada???
    # tara = Column(Numeric(10))
    listaSemirreboque = []
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
        self.listaSemirreboque = []
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


class ConteinerUld(BaseDumpable):
    __tablename__ = 'conteineresuld'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    num = Column(String(11))
    tipo = Column(String(5))
    vazio = Column(Boolean)
    ocrNum = Column(Boolean)
    numBooking = Column(String(20))
    listaLacres = []
    avaria = Column(Boolean)
    portoDescarga = Column(String(40))
    destinoCarga = Column(String(40))
    imoNavio = Column(String(40))
    cnpjCliente = Column(String(14))
    nmCliente = Column(String(100))
    acessoveiculo_id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                              ForeignKey('acessosveiculo.id'))
    acessoveiculo = relationship(
        'AcessoVeiculo'  # , backref=backref('listaConteineresUld')
    )

    @validates('numBooking', 'portoDescarga', 'destinoCarga', 'imoNavio', 'nmCliente')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value

class Semirreboque(BaseDumpable):
    __tablename__ = 'semirreboques'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    placa = Column(String(7))
    tara = Column(Numeric(5))
    pesagemveiculo_id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                              ForeignKey('pesagensveiculo.id'))
    pesagens = relationship(
        'PesagemVeiculo'  # , backref=backref('listaConteineresUld')
    )

    @validates('placa')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


if __name__ == '__main__':
    engine = Production.sql
    # Base.metadata.drop_all(engine, [])
    Base.metadata.create_all(engine)



