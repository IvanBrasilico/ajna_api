# Tescases for ajnaapi Puxador de Eventos extras API Recintos
import unittest
from datetime import datetime
from unittest import mock

from sqlalchemy.orm import scoped_session, sessionmaker

from ajnaapi.config import Testing
from ajnaapi.poll_events import Base, EventPoll, ControleEvento, ProcessaEvento
from ajnaapi.recintosapi.models_extra import AgendamentoConferencia

RECINTO1 = 'DTE'
RECINTO2 = 'CRAGEA'


def mocked_requests_get_new(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data = '2020-01-02'
    dataagenda = '2020-01-05'
    agendamento = AgendamentoConferencia(idEvento=1,
                                         dtHrOcorrencia=data,
                                         cpfOperOcor='1',
                                         dtHrRegistro=data,
                                         cpfOperReg='1',
                                         protocoloEventoRetifCanc=None,
                                         contingencia=False,
                                         recinto=RECINTO1,
                                         dtHrAgenda=dataagenda)
    return MockResponse([agendamento.dump()], 200)


class PollTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = Testing.sql
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                                      autoflush=False,
                                                      bind=self.engine))
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        # self.session.remove()
        pass

    def create_controle(self):
        controle = ControleEvento()
        controle.tipoevento = AgendamentoConferencia.__name__
        controle.recinto = RECINTO1
        controle.lastdate = datetime(2010, 1, 1)
        self.db_session.add(controle)
        self.db_session.commit()
        return controle

    def test_controle(self):
        controle = self.create_controle()
        controle_ = self.db_session.query(ControleEvento.lastdate).filter(
            ControleEvento.recinto == controle.recinto
        ).filter(
            ControleEvento.tipoevento == AgendamentoConferencia.__name__
        ).first()
        assert controle_.lastdate == controle.lastdate

    @mock.patch('requests.get', side_effect=mocked_requests_get_new)
    def test_processa_evento_get_new(self, mock_get):
        processa_evento = ProcessaEvento(AgendamentoConferencia, RECINTO1)
        agendamentos = processa_evento.get_new(self.db_session)
        controle = self.create_controle()
        agendamentos = processa_evento.get_new(self.db_session)

    @mock.patch('requests.get', side_effect=mocked_requests_get_new)
    def test_poll(self, mock_get):
        event_poll = EventPoll(Testing, sleep_time=1)
        event_poll.add_event_type(AgendamentoConferencia, RECINTO1)
        event_poll.active = False
        event_poll.make_poll(self.db_session)
        # Deve existir no banco o agendamento criado no request mock, pois make_poll
        # salvará o json de mocked_requests_get_new em new_events e chamará save_tomodel
        # nestes Eventos
        agendamentos = self.db_session.query(AgendamentoConferencia).all()
        assert len(agendamentos) == 1
        agendamento_polled = agendamentos[0]
        assert agendamento_polled.recinto == RECINTO1
        assert agendamento_polled.cpfOperOcor == '1'
        assert agendamento_polled.contingencia is False
        assert agendamento_polled.protocoloEventoRetifCanc is None

