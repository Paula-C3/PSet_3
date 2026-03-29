import pytest               #type: ignore
from datetime import datetime, timezone

from backend.domain.entities import User, Incident, Task, Notification
from backend.domain.enums import (
    EventType,
    IncidentStatus,
    NotificationChannel,
    NotificationStatus,
    Role,
    Severity,
    TaskStatus,
)
from backend.domain.state import InvalidTransitionError


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def user():
    return User(
        name="Ana Torres",
        email="ana@opscenter.com",
        hashed_password="hashed_secret",
        role=Role.OPERATOR,
    )


@pytest.fixture
def incident():
    return Incident(
        title="DB latency spike",
        description="p99 latency above 2s on prod",
        severity=Severity.HIGH,
        created_by="user-123",
    )


@pytest.fixture
def task(incident):
    return Task(
        incident_id=incident.id,
        title="Check slow queries",
        description="Run EXPLAIN on the flagged queries",
        assigned_to="user-456",
    )


@pytest.fixture
def notification(user):
    return Notification(
        recipient=user.id,
        channel=NotificationChannel.IN_APP,
        message="You have been assigned an incident.",
        event_type=EventType.INCIDENT_ASSIGNED,
    )


# ── User ─────────────────────────────────────────────────────────────

class TestUser:

    def test_creates_with_required_fields(self, user):
        assert user.name == "Ana Torres"
        assert user.email == "ana@opscenter.com"
        assert user.role == Role.OPERATOR

    def test_auto_generates_id(self, user):
        assert user.id is not None
        assert len(user.id) > 0

    def test_two_users_get_different_ids(self):
        u1 = User(name="A", email="a@x.com", hashed_password="h", role=Role.ADMIN)
        u2 = User(name="B", email="b@x.com", hashed_password="h", role=Role.ADMIN)
        assert u1.id != u2.id

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="name"):
            User(name="   ", email="a@x.com", hashed_password="h", role=Role.OPERATOR)

    def test_rejects_invalid_email(self):
        with pytest.raises(ValueError, match="email"):
            User(name="Ana", email="not-an-email", hashed_password="h", role=Role.OPERATOR)


# ── Incident ──────────────────────────────────────────────────────────

class TestIncident:

    def test_creates_with_required_fields(self, incident):
        assert incident.title == "DB latency spike"
        assert incident.severity == Severity.HIGH
        assert incident.created_by == "user-123"

    def test_default_status_is_open(self, incident):
        assert incident.status == IncidentStatus.OPEN

    def test_assigned_to_is_none_by_default(self, incident):
        assert incident.assigned_to is None

    def test_auto_generates_id(self, incident):
        assert incident.id is not None

    def test_created_at_is_timezone_aware(self, incident):
        assert incident.created_at.tzinfo is not None

    def test_rejects_empty_title(self):
        with pytest.raises(ValueError, match="title"):
            Incident(title="  ", description="desc", severity=Severity.LOW, created_by="u1")

    def test_rejects_empty_description(self):
        with pytest.raises(ValueError, match="description"):
            Incident(title="Title", description="  ", severity=Severity.LOW, created_by="u1")

    def test_assign_sets_assignee_and_status(self, incident):
        incident.assign("user-999")
        assert incident.assigned_to == "user-999"
        assert incident.status == IncidentStatus.ASSIGNED

    def test_full_lifecycle(self, incident):
        incident.assign("user-999")
        incident.start_progress()
        assert incident.status == IncidentStatus.IN_PROGRESS
        incident.resolve()
        assert incident.status == IncidentStatus.RESOLVED
        incident.close()
        assert incident.status == IncidentStatus.CLOSED

    def test_invalid_transition_raises(self, incident):
        with pytest.raises(InvalidTransitionError):
            incident.start_progress()  # OPEN -> IN_PROGRESS is not allowed

    def test_closed_incident_rejects_all_transitions(self, incident):
        incident.assign("u1")
        incident.start_progress()
        incident.resolve()
        incident.close()
        with pytest.raises(InvalidTransitionError):
            incident.assign("u2")

    def test_reassignment_allowed_while_assigned(self, incident):
        incident.assign("user-1")
        incident.assign("user-2")
        assert incident.assigned_to == "user-2"
        assert incident.status == IncidentStatus.ASSIGNED

    def test_reassignment_allowed_while_in_progress(self, incident):
        incident.assign("user-1")
        incident.start_progress()
        incident.assign("user-2")
        assert incident.assigned_to == "user-2"
        assert incident.status == IncidentStatus.IN_PROGRESS


# ── Task ──────────────────────────────────────────────────────────────

class TestTask:

    def test_creates_with_required_fields(self, task, incident):
        assert task.incident_id == incident.id
        assert task.title == "Check slow queries"
        assert task.assigned_to == "user-456"

    def test_default_status_is_open(self, task):
        assert task.status == TaskStatus.OPEN

    def test_auto_generates_id(self, task):
        assert task.id is not None

    def test_created_at_is_timezone_aware(self, task):
        assert task.created_at.tzinfo is not None

    def test_rejects_empty_title(self, incident):
        with pytest.raises(ValueError, match="title"):
            Task(incident_id=incident.id, title="  ", description="d", assigned_to="u1")

    def test_rejects_empty_description(self, incident):
        with pytest.raises(ValueError, match="description"):
            Task(incident_id=incident.id, title="T", description="  ", assigned_to="u1")


# ── Notification ──────────────────────────────────────────────────────

class TestNotification:

    def test_creates_with_required_fields(self, notification, user):
        assert notification.recipient == user.id
        assert notification.channel == NotificationChannel.IN_APP
        assert notification.event_type == EventType.INCIDENT_ASSIGNED

    def test_default_status_is_pending(self, notification):
        assert notification.status == NotificationStatus.PENDING

    def test_auto_generates_id(self, notification):
        assert notification.id is not None

    def test_created_at_is_timezone_aware(self, notification):
        assert notification.created_at.tzinfo is not None

    def test_mark_sent(self, notification):
        notification.mark_sent()
        assert notification.status == NotificationStatus.SENT

    def test_mark_failed(self, notification):
        notification.mark_failed()
        assert notification.status == NotificationStatus.FAILED