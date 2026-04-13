from backend.domain.enums import EventType, NotificationChannel
from backend.domain.templates import EmailNotificationTemplate, InAppNotificationTemplate


def test_email_template_contiene_asunto():
    template = EmailNotificationTemplate()
    mensaje = template.build_message(EventType.INCIDENT_CREATED, {"id": "123"})
    assert "Asunto" in mensaje
    assert "INCIDENT_CREATED" in mensaje
    assert "OpsCenter" in mensaje


def test_inapp_template_formato_compacto():
    template = InAppNotificationTemplate()
    mensaje = template.build_message(EventType.TASK_DONE, {"task_id": "abc"})
    assert "TASK_DONE" in mensaje
    assert "task_id" in mensaje
    assert "OpsCenter" in mensaje


def test_templates_producen_formatos_diferentes():
    email = EmailNotificationTemplate()
    inapp = InAppNotificationTemplate()
    payload = {"id": "999"}
    msg_email = email.build_message(EventType.INCIDENT_ASSIGNED, payload)
    msg_inapp = inapp.build_message(EventType.INCIDENT_ASSIGNED, payload)
    assert msg_email != msg_inapp