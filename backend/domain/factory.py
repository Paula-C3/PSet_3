from backend.domain.entities import Incident, Notification
from backend.domain.enums import EventType, NotificationChannel, Severity
from backend.domain.commands import Command, SendEmailCommand, SendInAppCommand
from backend.domain.templates import EmailNotificationTemplate, InAppNotificationTemplate, NotificationTemplate

class IncidentFactory:
    """Crea incidentes validando todos los campos requeridos"""

    @staticmethod
    def create(title: str, description: str, severity: str, created_by: str) -> Incident:
        if not title.strip():
            raise ValueError("El título no puede estar vacío")
        if not description.strip():
            raise ValueError("La descripción no puede estar vacía")
        if severity not in Severity._value2member_map_:
            raise ValueError(f"Severidad inválida: {severity}")
        return Incident(
            title=title,
            description=description,
            severity=Severity(severity),
            created_by=created_by,
        )


class NotificationFactory:
    """Abstract Factory: crea el comando y template correctos según el canal"""

    @staticmethod
    def create_command(notification: Notification) -> Command:
        if notification.channel == NotificationChannel.EMAIL:
            return SendEmailCommand(notification)
        if notification.channel == NotificationChannel.IN_APP:
            return SendInAppCommand(notification)
        raise ValueError(f"Canal no soportado: {notification.channel}")

    @staticmethod
    def create_template(channel: NotificationChannel) -> NotificationTemplate:
        if channel == NotificationChannel.EMAIL:
            return EmailNotificationTemplate()
        if channel == NotificationChannel.IN_APP:
            return InAppNotificationTemplate()
        raise ValueError(f"Canal no soportado: {channel}")