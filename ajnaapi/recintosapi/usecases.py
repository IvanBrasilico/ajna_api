import logging

from sqlalchemy.orm import load_only

from ajnaapi.recintosapi import maschemas
from ajnaapi.recintosapi import models as orm


class UseCases:

    def __init__(self, db_session):
        """Init.

        :param db_session: Conexao ao Banco
        """
        self.db_session = db_session
        self.eventos_com_filhos = {
            orm.AcessoVeiculo: self.load_acessoveiculo,
        }

    def allowed_file(self, filename, extensions):
        """Checa extensões permitidas."""
        return '.' in filename and \
               filename.rsplit('.', 1)[-1].lower() in extensions

    def valid_file(self, file, extensions=['jpg', 'xml', 'json']) -> [bool, str]:
        """Valida arquivo. Retorna resultado(True/False) e mensagem de erro."""
        erro = None
        if not file:
            erro = 'Arquivo nao informado'
        elif not file.filename:
            erro = 'Nome do arquivo vazio'
        elif not self.allowed_file(file.filename, extensions):
            erro = 'Nome de arquivo não permitido: ' + \
                   file.filename
        return erro is None, erro

    def insert_evento(self, aclass, evento: dict, commit=True) -> orm.EventoBase:
        logging.info('Creating evento %s %s' %
                     (aclass.__name__,
                      evento.get('idEvento'))
                     )
        novo_evento = aclass(**evento)

        self.db_session.add(novo_evento)
        if commit:
            self.db_session.commit()
        else:
            self.db_session.flush()
        self.db_session.refresh(novo_evento)
        return novo_evento

    def load_evento(self, aclass, recinto: str, IDEvento: int,
                    fields: list = None) -> orm.EventoBase:
        """
        Retorna Evento classe aclass encontrado único com recinto E IDEvento.

        Levanta exceção NoResultFound(não encontrado) ou MultipleResultsFound.

        :param aclass: Classe ORM que acessa o BD
        :param IDEvento: ID do Evento informado pelo recinto
        :param fields: Trazer apenas estes campos
        :return: objeto
        """
        query = self.db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento,
            aclass.recinto == recinto
        )
        if fields and isinstance(fields, list) and len(fields) > 0:
            query = query.options(load_only(fields))
        evento = query.one()
        return evento

    def get_filhos(self, osfilhos, campos_excluidos=[]):
        filhos = []
        if osfilhos and len(osfilhos) > 0:
            for filho in osfilhos:
                filhos.append(
                    filho.dump(
                        exclude=campos_excluidos)
                )
        return filhos

    def insert_filhos(self, oevento, osfilhos, classefilho, fk_no_filho):
        """Processa lista no campo 'campofilhos' para inserir aclasse.

        :param oevento: dict com valores recebidos do JSON
        :param campofilhos: nome do campo que contem filhos do evento
        :param aclasse: Nome da Classe a criar
        :param fk_no_filho: Nome do campo que referencia pai na Classe filha
        :return: None, apenas levanta exceção se acontecer
        """
        for filho in osfilhos:
            params = {**{fk_no_filho: oevento}, **filho}
            novofilho = classefilho(**params)
            self.db_session.add(novofilho)

    def load_acessoveiculo(self, recinto: str, idEvento: str) -> dict:
        try:
            acessoveiculo = self.db_session.query(orm.AcessoVeiculo).filter(
                orm.AcessoVeiculo.idEvento == idEvento
            ).filter(
                orm.AcessoVeiculo.recinto == recinto
            ).outerjoin(
                orm.ConteinerUld
            ).first()
            acessoveiculo_schema = maschemas.AcessoVeiculo()
            # print('*******', acessoveiculo.dump())
            data = acessoveiculo_schema.dump(acessoveiculo)
            return data
        except Exception as err:
            logging.error(err, exc_info=True)
            raise (err)

    def insert_acessoveiculo(self, evento: dict) -> orm.AcessoVeiculo:
        logging.info('Creating acessoveiculo %s..', evento.get('idEvento'))
        try:
            # print(evento)
            acessoveiculo = self.insert_evento(orm.AcessoVeiculo, evento)
            # print(acessoveiculo)
            listaConteineresUld = evento.get('listaContainersUld')
            if listaConteineresUld:
                for conteiner in listaConteineresUld:
                    # logging.info('Creating conteiner %s..', conteiner.get('num'))
                    conteiner['acessoveiculo_id'] = acessoveiculo.id
                    conteineruld = orm.ConteinerUld(**conteiner)
                    # print(conteineruld.dump())
                    self.db_session.add(conteineruld)
            self.db_session.commit()
        except Exception as err:
            logging.error(err, exc_info=True)
            self.db_session.rollback()
            raise (err)
        return acessoveiculo

    def load_pesagemveiculo(self, recinto: str, idEvento: str) -> dict:
        try:
            pesagemveiculo = self.db_session.query(orm.PesagemVeiculo).filter(
                orm.PesagemVeiculo.idEvento == idEvento
            ).filter(
                orm.PesagemVeiculo.recinto == recinto
            ).outerjoin(
                orm.Semirreboque
            ).first()
            pesagemveiculo_schema = maschemas.PesagemVeiculo()
            # print('*******', pesagemveiculo.dump())
            data = pesagemveiculo_schema.dump(pesagemveiculo)
            return data
        except Exception as err:
            logging.error(err, exc_info=True)
            raise (err)

    def insert_pesagemveiculo(self, evento: dict) -> orm.PesagemVeiculo:
        logging.info('Creating pesagemveiculo %s..', evento.get('idEvento'))
        try:
            # print(evento)
            pesagemveiculo = self.insert_evento(orm.PesagemVeiculo, evento)
            # print(pesagemveiculo)
            listaSemirreboque = evento.get('listaSemirreboque')
            if listaSemirreboque:
                for reboque in listaSemirreboque:
                    # logging.info('Creating conteiner %s..', conteiner.get('num'))
                    reboque['pesagemveiculo_id'] = pesagemveiculo.id
                    semirreboque = orm.Semirreboque(**reboque)
                    self.db_session.add(semirreboque)
            self.db_session.commit()
        except Exception as err:
            logging.error(err, exc_info=True)
            self.db_session.rollback()
            raise (err)
        return pesagemveiculo
