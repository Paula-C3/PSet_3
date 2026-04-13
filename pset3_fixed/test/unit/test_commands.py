from backend.domain.entities import Notification
from backend.domain.enums import EventType, NotificationChannel, NotificationStatus
from backend.domain.commands import SendEmailCommand, SendInAppCommand


def test_send_email_command_ejecuta_y_marca_enviado():
    notif = Notification(
        recipient="user-1",
        channel=NotificationChannel.EMAIL,
        message="Incidente creado",
        event_type=EventType.INCIDENT_CREATED,
    )
    cmd = SendEmailCommand(notif)
    cmd.execute()
    assert notif.status == NotificationStatus.SENT


def test_send_inapp_command_ejecuta_y_marca_enviado():
    notif = Notification(
        recipient="user-2",
        channel=NotificationChannel.IN_APP,
        message="Tarea asignada",
        event_type=EventType.TASK_CREATED,
    )
    cmd = SendInAppCommand(notif)
    cmd.execute()
    assert notif.status == NotificationStatus.SENT