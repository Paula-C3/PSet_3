from abc import ABC, abstractmethod
from backend.domain.enums import EventType

class NotificationTemplate(ABC):
    """Template Method: define el esqueleto del mensaje de notificación"""

    def build_message(self, event_type: EventType, payload: dict) -> str:
        header = self._header(event_type)
        body = self._body(payload)
        footer = self._footer()
        return f"{header}\n{body}\n{footer}"

    @abstractmethod
    def _header(self, event_type: EventType) -> str:
        pass

    @abstractmethod
    def _body(self, payload: dict) -> str:
        pass

    def _footer(self) -> str:
        return "-- OpsCenter"


class EmailNotificationTemplate(NotificationTemplate):
    """Construye mensajes con formato para EMAIL"""

    def _header(self, event_type: EventType) -> str:
        return f"Asunto: Notificación OpsCenter - {event_type.value}"

    def _body(self, payload: dict) -> str:
        lines = [f"  {k}: {v}" for k, v in payload.items()]
        return "Detalles:\n" + "\n".join(lines)


class InAppNotificationTemplate(NotificationTemplate):
    """Construye mensajes con formato para IN_APP"""

    def _header(self, event_type: EventType) -> str:
        return f"[{event_type.value}]"

    def _body(self, payload: dict) -> str:
        return " | ".join(f"{k}={v}" for k, v in payload.items())