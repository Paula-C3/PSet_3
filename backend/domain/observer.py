from abc import ABC, abstractmethod
from typing import List
from backend.domain.entities import Notification
from backend.domain.enums import EventType, NotificationChannel, NotificationStatus

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
    def __init__(self, notification_repo):
        self.notification_repo = notification_repo

    def handle(self, event_type: EventType, payload: dict) -> None:
        print(f"[NotificationObserver] Evento: {event_type.value} | payload: {payload}")
        
        recipient = payload.get("assigned_to") or payload.get("created_by") or payload.get("id")
        
        notification = Notification(
            recipient = payload.get("assigned_to") or payload.get("created_by") or payload.get("id") or "system",
            channel=NotificationChannel.IN_APP,
            message=f"Evento {event_type.value}: {payload}",
            event_type=event_type,
            status=NotificationStatus.SENT,
        )
        self.notification_repo.save(notification)

class LogObserver(Observer):
    """Registra todos los eventos del sistema en consola"""

    def handle(self, event_type: EventType, payload: dict) -> None:
        print(f"[LogObserver] {event_type.value} → {payload}")