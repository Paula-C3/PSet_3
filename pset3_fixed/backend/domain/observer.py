from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from backend.domain.enums import EventType


class Observer(ABC):
    @abstractmethod
    def handle(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        pass


class EventBus:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def publish(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.handle(event_type, payload)


class NotificationObserver(Observer):
    def __init__(self, notification_repo) -> None:
        self.notification_repo = notification_repo

    def handle(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        recipient = payload.get("assigned_to") or payload.get("created_by")

        if not recipient:
            print(f"[NotificationObserver] No recipient for event {event_type.value}")
            return

        from backend.domain.entities import Notification
        from backend.domain.enums import NotificationChannel, NotificationStatus

        notification = Notification(
            recipient=recipient,
            channel=NotificationChannel.IN_APP,
            message=f"Evento {event_type.value}: {payload}",
            event_type=event_type,
            status=NotificationStatus.PENDING,
        )

        self.notification_repo.save(notification)


class LogObserver(Observer):
    def handle(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        print(f"[EVENT] {event_type.value} - {payload}")