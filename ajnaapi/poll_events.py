"""AJNA precisar definir Eventos extras de integração que não estão na API Recintos.

(ex. Agendamento de Conferência, Verificação Física, Fotos de verificação física)

Estes Eventos extras não terão "push" por parte dos Recintos. Assim, será realizado um
"pull" através de um endpoit disponibilizado pelo Recinto. Evento será consultado de
tempos em tempos por um poll de dados.

Este poll pode ser utilizado para outras integrações, como a própria "puxada" da
API Recintos.

"""
import time
from datetime import datetime
from typing import List

import requests
from sqlalchemy import Column, BigInteger, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session

from ajna_commons.flask.log import logger
from ajnaapi.config import Production
from ajnaapi.recintosapi.models import Base, EventoBase
from ajnaapi.recintosapi.models_extra import AgendamentoConferencia


class ControleEvento(Base):
    __tablename__ = 'recinto_controle'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    recinto = Column(String(10))
    tipoevento = Column(String(20))
    lastdate = Column(DateTime)


class ProcessaEvento():
    def __init__(self, evento: EventoBase, recinto: str):
        self.evento: EventoBase = evento
        self.recinto: str = recinto

    def get_lastdate(self, db_session):
        _controle = db_session.query(ControleEvento.lastdate).filter(
            ControleEvento.recinto == self.recinto
        ).filter(
            ControleEvento.tipoevento == self.evento.__name__
        ).first()
        if _controle:
            return _controle.lastdate
        return datetime(2020, 1, 1)

    def get_new(self, db_session):
        lastdate = self.get_lastdate(db_session)
        data = datetime.strftime(lastdate, '%Y%m%dT%H:%M:%S')
        self.new_events = requests.get(self.recinto + data).json()

    def save_tomodel(self, db_session):
        for event in self.new_events:
            try:
                instance = self.evento(**event)
                db_session.add(instance)
                db_session.commit()
                self.last_date = instance.dtHrOcorrencia
            except Exception as err:
                logger.error('Erro ao inserir Evento Tipo: {} Conteúdo: {}'.format(
                    self.evento.__name__, event))
                logger.error(str(err))

    def process(self, db_session):
        self.get_new(db_session)
        self.save_tomodel(db_session)


class EventPoll():
    def __init__(self, configclass, sleep_time=10):
        self.configclass = configclass
        self.sleep_time = sleep_time
        self.processa_eventos: List[ProcessaEvento] = []
        self.active = True

    def add_event_type(self, model, recinto):
        self.processa_eventos.append(ProcessaEvento(model, recinto))

    def process_poll(self, db_session):
        for processa_evento in self.processa_eventos:
            processa_evento.process(db_session)

    def make_poll(self, db_session):
        # mongodb = self.configclass.db
        self.process_poll(db_session)
        while self.active:
            self.process_poll(db_session)
            time.sleep(self.sleep_time)


if __name__ == '__main__':  # pragma: no cover
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=Production.sql))
    # Base.metadata.create_all(Production.sql)
    poll = EventPoll(Production, sleep_time=1)
    poll.add_event_type(AgendamentoConferencia, 'agendamentosconferencias')
    poll.make_poll(db_session)
