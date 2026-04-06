from abc import ABC, abstractmethod
from typing import List
from domain.enums import EventType


class Observer(ABC):
    @abstractmethod
    def handle(self, event_type: EventType, payload: dict) -> None:
        pass


class EventBus:
    def __init__(self):
        self._observers: List[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def publish(self, event_type: EventType, payload: dict) -> None:
        for observer in self._observers:
            observer.handle(event_type, payload)


class NotificationObserver(Observer):
    """Reacciona a eventos y genera notificaciones"""

    def handle(self, event_type: EventType, payload: dict) -> None:
        print(f"[NotificationObserver] Evento: {event_type.value} | payload: {payload}")


class LogObserver(Observer):
    """Registra todos los eventos del sistema en consola"""

    def handle(self, event_type: EventType, payload: dict) -> None:
        print(f"[LogObserver] {event_type.value} → {payload}")