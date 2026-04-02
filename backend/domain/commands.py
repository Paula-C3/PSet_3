from abc import ABC, abstractmethod
from backend.domain.entities import Notification
from backend.domain.enums import NotificationChannel


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class SendEmailCommand(Command):
    """Envía una notificación por canal EMAIL"""

    def __init__(self, notification: Notification) -> None:
        self._notification = notification

    def execute(self) -> None:
        print(f"[EMAIL] Para: {self._notification.recipient} | {self._notification.message}")
        self._notification.mark_sent()


class SendInAppCommand(Command):
    """Envía una notificación por canal IN_APP"""

    def __init__(self, notification: Notification) -> None:
        self._notification = notification

    def execute(self) -> None:
        print(f"[IN_APP] Para: {self._notification.recipient} | {self._notification.message}")
        self._notification.mark_sent()