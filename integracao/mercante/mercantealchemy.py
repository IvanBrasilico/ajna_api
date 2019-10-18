# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Column, CHAR, \
    DateTime, func, Integer, MetaData, Table, Text
from sqlalchemy.dialects.mysql import BIGINT, TIMESTAMP

from ajna_commons.flask.conf import SQL_URI

metadata = MetaData()

# Tabelas de lista do XML
t_ConteinerVazio = Table(
    'ConteinerVazio', metadata,
    Column('index', BIGINT(20), index=True),
    Column('idConteinerVazio', Text),
    Column('isoConteinerVazio', Text),
    Column('manifesto', Text),
    Column('taraConteinerVazio', Text),
    Column('tipoMovimento', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

t_NCMItemCarga = Table(
    'NCMItemCarga', metadata,
    Column('index', BIGINT(20), index=True),
    Column('codigoConteiner', Text),
    Column('codigoTipoEmbalagem', Text),
    Column('descritivo', Text),
    Column('identificacaoNCM', Text),
    Column('itemEmbaladoMadeira', Text),
    Column('marcaMercadoria', Text),
    Column('numeroCEMercante', Text),
    Column('numeroIdentificacao', Text),
    Column('numeroSequencialItemCarga', Text),
    Column('qtdeVolumes', Text),
    Column('tipoMovimento', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

# Tabelas base do XML
t_conhecimentosEmbarque = Table(
    'conhecimentosEmbarque', metadata,
    Column('index', BIGINT(20), index=True),
    Column('codigoEmpresaNavegacao', Text),
    Column('codigoTerminalCarregamento', Text),
    Column('consignatario', Text),
    Column('cubagem', Text),
    Column('dataAtualizacao', Text),
    Column('dataEmissao', Text),
    Column('descricao', Text),
    Column('embarcador', Text),
    Column('horaAtualizacao', Text),
    Column('indicadorShipsConvenience', Text),
    Column('manifestoCE', Text),
    Column('numeroCEMaster', Text),
    Column('numeroCEmercante', Text),
    Column('paisDestinoFinalMercante', Text),
    Column('portoDestFinal', Text),
    Column('portoOrigemCarga', Text),
    Column('tipoBLConhecimento', Text),
    Column('tipoMovimento', Text),
    Column('tipoTrafego', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

t_exclusoesEscala = Table(
    'exclusoesEscala', metadata,
    Column('index', BIGINT(20), index=True),
    Column('dataExclusao', Text),
    Column('horaExclusao', Text),
    Column('numeroEscalaMercante', Text),
    Column('tipoMovimento', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

t_itensCarga = Table(
    'itensCarga', metadata,
    Column('index', BIGINT(20), index=True),
    Column('NCM', Text),
    Column('codigoConteiner', Text),
    Column('codigoTipoEmbalagem', Text),
    Column('contraMarca', Text),
    Column('cubagemM3', Text),
    Column('dataAtualizacao', Text),
    Column('horaAtualizacao', Text),
    Column('indicadorUsoParcial', Text),
    Column('isoCode', Text),
    Column('lacre', Text),
    Column('marca', Text),
    Column('numeroCEmercante', Text),
    Column('numeroSequencialItemCarga', Text),
    Column('pesoBruto', Text),
    Column('qtdeItens', Text),
    Column('tara', Text),
    Column('tipoItemCarga', Text),
    Column('tipoMovimento', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

t_manifestosCarga = Table(
    'manifestosCarga', metadata,
    Column('index', BIGINT(20), index=True),
    Column('codAgenciaInformante', Text),
    Column('codigoEmpresaNavegacao', Text),
    Column('codigoTerminalCarregamento', Text),
    Column('codigoTerminalDescarregamento', Text),
    Column('dataAtualizacao', Text),
    Column('dataEncerramento', Text),
    Column('dataInicioOperacao', Text),
    Column('horaAtualizacao', Text),
    Column('numero', Text),
    Column('numeroImoDPC', Text),
    Column('numeroViagem', Text),
    Column('portoCarregamento', Text),
    Column('portoDescarregamento', Text),
    Column('quantidadeConhecimento', Text),
    Column('tipoMovimento', Text),
    Column('tipoTrafego', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp())
)

### Tabelas resumo

conhecimentos = Table(
    'conhecimentos', metadata,
    Column('ID', BigInteger().with_variant(Integer, "sqlite"),
           primary_key=True, autoincrement=True),
    Column('codigoEmpresaNavegacao', Text),
    Column('codigoTerminalCarregamento', Text),
    Column('consignatario', CHAR(15)),
    Column('cubagem', Text),
    Column('dataAtualizacao', Text),
    Column('dataEmissao', Text),
    Column('descricao', Text),
    Column('embarcador', Text),
    Column('horaAtualizacao', Text),
    Column('indicadorShipsConvenience', Text),
    Column('manifestoCE', CHAR(15)),
    Column('numeroCEMaster', CHAR(15)),
    Column('numeroCEmercante', CHAR(15), unique=True),
    Column('paisDestinoFinalMercante', Text),
    Column('portoDestFinal', Text),
    Column('portoOrigemCarga', Text),
    Column('tipoBLConhecimento', Text),
    Column('tipoTrafego', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, onupdate=func.current_timestamp())
)

manifestos = Table(
    'manifestos', metadata,
    Column('ID', BigInteger().with_variant(Integer, "sqlite"),
           primary_key=True, autoincrement=True),
    Column('codAgenciaInformante', Text),
    Column('codigoEmpresaNavegacao', Text),
    Column('codigoTerminalCarregamento', Text),
    Column('codigoTerminalDescarregamento', Text),
    Column('dataAtualizacao', Text),
    Column('dataEncerramento', Text),
    Column('dataInicioOperacao', Text),
    Column('horaAtualizacao', Text),
    Column('numero', CHAR(15), unique=True),
    Column('numeroImoDPC', Text),
    Column('numeroViagem', Text),
    Column('portoCarregamento', Text),
    Column('portoDescarregamento', Text),
    Column('quantidadeConhecimento', Text),
    Column('tipoTrafego', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, onupdate=func.current_timestamp())
)

itens = Table(
    'itens', metadata,
    Column('ID', BigInteger().with_variant(Integer, "sqlite"),
           primary_key=True, autoincrement=True), \
    # TODO: Confirmar que chave é esta
    # A chave aqui é composta
    # Provavelmente numeroCEmercante + numeroSequencialItemCarga
    Column('numeroCEmercante', CHAR(15), index=True),
    Column('numeroSequencialItemCarga', CHAR(5), index=True),
    Column('codigoConteiner', CHAR(11)),
    Column('NCM', CHAR(4)),
    Column('codigoTipoEmbalagem', Text),
    Column('contraMarca', Text),
    Column('cubagemM3', Text),
    Column('dataAtualizacao', Text),
    Column('horaAtualizacao', Text),
    Column('indicadorUsoParcial', Text),
    Column('isoCode', Text),
    Column('lacre', Text),
    Column('marca', Text),
    Column('numeroCEmercante', CHAR(15)),
    Column('pesoBruto', Text),
    Column('qtdeItens', Text),
    Column('tara', Text),
    Column('tipoItemCarga', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, onupdate=func.current_timestamp())
)

NCMItem = Table(
    'NCMItem', metadata,
    Column('ID', BigInteger().with_variant(Integer, "sqlite"),
           primary_key=True, autoincrement=True),
    # TODO: Confirmar que chave é esta
    # A chave aqui é composta
    # Provavelmente numeroCEmercante + numeroSequencialItemCarga
    Column('numeroCEMercante', CHAR(15), index=True),
    Column('numeroSequencialItemCarga', CHAR(5), index=True),
    Column('codigoConteiner', CHAR(11), index=True),
    Column('identificacaoNCM', CHAR(4), index=True),
    Column('codigoTipoEmbalagem', Text),
    Column('descritivo', Text),
    Column('identificacaoNCM', Text),
    Column('itemEmbaladoMadeira', Text),
    Column('marcaMercadoria', Text),
    Column('numeroIdentificacao', Text),
    Column('qtdeVolumes', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, onupdate=func.current_timestamp())
)

conteineresVazios = Table(
    'conteineresVazio', metadata,
    Column('ID', BigInteger().with_variant(Integer, "sqlite"),
           primary_key=True, autoincrement=True),
    Column('manifesto', CHAR(15), index=True),
    Column('idConteinerVazio', CHAR(11), index=True),
    Column('isoConteinerVazio', Text),
    Column('taraConteinerVazio', Text),
    Column('create_date', TIMESTAMP, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, onupdate=func.current_timestamp())
)

if __name__ == '__main__':
    confirma = input('Recriar todas as tabelas ** APAGA TODOS OS DADOS ** (S/N)')
    if confirma != 'S':
        exit('Saindo... (só recrio se digitar "S", digitou %s)' % confirma)
    print('Recriando tabelas, aguarde...')
    # engine = create_engine('mysql+pymysql://ivan@localhost:3306/mercante')
    banco = input('Escolha a opção de Banco (1 - MySQL/ 2 - Sqlite)')
    if banco == '1':
        engine = create_engine(SQL_URI)
        metadata.drop_all(engine)
        metadata.create_all(engine)
    if banco == '2':
        engine = create_engine('sqlite:///teste.db')
        metadata.drop_all(engine)
        metadata.create_all(engine)
