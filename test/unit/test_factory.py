import pytest
from backend.domain.enums import EventType, NotificationChannel, Severity
from backend.domain.entities import Notification
from backend.domain.factory import IncidentFactory, NotificationFactory
from backend.domain.commands import SendEmailCommand, SendInAppCommand
from backend.domain.templates import EmailNotificationTemplate, InAppNotificationTemplate

def test_incident_factory_crea_incidente_valido():
    incident = IncidentFactory.create(
        title="Servidor caído",
        description="El servidor principal no responde",
        severity="HIGH",
        created_by="user-1",
    )
    assert incident.title == "Servidor caído"
    assert incident.severity == Severity.HIGH


def test_incident_factory_rechaza_titulo_vacio():
    with pytest.raises(ValueError):
        IncidentFactory.create(
            title="",
            description="Descripción válida",
            severity="LOW",
            created_by="user-1",
        )


def test_incident_factory_rechaza_severidad_invalida():
    with pytest.raises(ValueError):
        IncidentFactory.create(
            title="Título válido",
            description="Descripción válida",
            severity="INVALIDA",
            created_by="user-1",
        )


def test_notification_factory_crea_comando_email():
    notif = Notification(
        recipient="user-1",
        channel=NotificationChannel.EMAIL,
        message="Hola",
        event_type=EventType.INCIDENT_CREATED,
    )
    cmd = NotificationFactory.create_command(notif)
    assert isinstance(cmd, SendEmailCommand)


def test_notification_factory_crea_comando_inapp():
    notif = Notification(
        recipient="user-1",
        channel=NotificationChannel.IN_APP,
        message="Hola",
        event_type=EventType.INCIDENT_CREATED,
    )
    cmd = NotificationFactory.create_command(notif)
    assert isinstance(cmd, SendInAppCommand)


def test_notification_factory_crea_template_email():
    template = NotificationFactory.create_template(NotificationChannel.EMAIL)
    assert isinstance(template, EmailNotificationTemplate)


def test_notification_factory_crea_template_inapp():
    template = NotificationFactory.create_template(NotificationChannel.IN_APP)
    assert isinstance(template, InAppNotificationTemplate)