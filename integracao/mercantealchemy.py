# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import Column, CHAR, DateTime, func, MetaData, Table, Text
from sqlalchemy.dialects.mysql import BIGINT

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
    Column('create_date', DateTime, server_default=func.current_timestamp())
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
    Column('create_date', DateTime, server_default=func.current_timestamp())
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
    Column('create_date', DateTime, server_default=func.current_timestamp())
)

t_exclusoesEscala = Table(
    'exclusoesEscala', metadata,
    Column('index', BIGINT(20), index=True),
    Column('dataExclusao', Text),
    Column('horaExclusao', Text),
    Column('numeroEscalaMercante', Text),
    Column('tipoMovimento', Text),
    Column('create_date', DateTime, server_default=func.current_timestamp())
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
    Column('create_date', DateTime, server_default=func.current_timestamp())
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
    Column('create_date', DateTime, server_default=func.current_timestamp())
)

### Tabelas resumo

conhecimentos = Table(
    'conhecimentos', metadata,
    Column('ID', BIGINT(20), primary_key=True, autoincrement=True),
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
    Column('numeroCEmercante', CHAR(15), unique=True),
    Column('paisDestinoFinalMercante', Text),
    Column('portoDestFinal', Text),
    Column('portoOrigemCarga', Text),
    Column('tipoBLConhecimento', Text),
    Column('tipoTrafego', Text),
    Column('create_date', DateTime, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, server_default=func.current_timestamp(),
           onupdate=func.current_timestamp())
)


manifestos = Table(
    'manifestos', metadata,
    Column('ID', BIGINT(20), primary_key=True, autoincrement=True),
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
    Column('create_date', DateTime, server_default=func.current_timestamp()),
    Column('last_modified', DateTime, server_default=func.current_timestamp(),
       onupdate=func.current_timestamp())
)


if __name__ == '__main__':
    confirma = input('Recriar todas as tabelas ** APAGA TODOS OS DADOS ** (S/N)')
    if confirma != 'S':
        exit('Saindo... (só recrio se digitar "S", digitou %s)' % confirma)
    print('Recriando tabelas, aguarde...')
    # engine = create_engine('mysql+pymysql://ivan@localhost:3306/mercante')
    engine = create_engine('sqlite:///teste.db')
    metadata.drop_all(engine)
    metadata.create_all(engine)
