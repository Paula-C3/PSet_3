from backend.domain.enums import EventType
from backend.domain.observer import EventBus, LogObserver, NotificationObserver


def test_eventbus_notifica_a_todos_los_observers():
    bus = EventBus()
    resultados = []

    class ObserverDePrueba(LogObserver):
        def handle(self, event_type, payload):
            resultados.append(event_type)

    obs1 = ObserverDePrueba()
    obs2 = ObserverDePrueba()
    bus.subscribe(obs1)
    bus.subscribe(obs2)
    bus.publish(EventType.INCIDENT_CREATED, {"id": "123"})

    assert len(resultados) == 2


def test_notification_observer_reacciona_a_evento(capsys):
    bus = EventBus()
    obs = NotificationObserver()
    bus.subscribe(obs)
    bus.publish(EventType.INCIDENT_ASSIGNED, {"incident_id": "abc"})
    captured = capsys.readouterr()
    assert "INCIDENT_ASSIGNED" in captured.out


def test_log_observer_registra_evento(capsys):
    obs = LogObserver()
    obs.handle(EventType.TASK_DONE, {"task_id": "xyz"})
    captured = capsys.readouterr()
    assert "TASK_DONE" in captured.out