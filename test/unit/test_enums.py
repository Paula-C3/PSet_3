import pytest           #type:ignore

from backend.domain.enums import (
    EventType,
    IncidentStatus,
    NotificationChannel,
    NotificationStatus,
    Role,
    Severity,
    TaskStatus,
)


class TestRole:

    def test_has_all_required_values(self):
        assert Role.ADMIN
        assert Role.SUPERVISOR
        assert Role.OPERATOR

    def test_has_exactly_three_roles(self):
        assert len(Role) == 3

    def test_is_string_compatible(self):
        assert Role.ADMIN == "ADMIN"
        assert Role.SUPERVISOR == "SUPERVISOR"
        assert Role.OPERATOR == "OPERATOR"


class TestSeverity:

    def test_has_all_required_values(self):
        assert Severity.LOW
        assert Severity.MEDIUM
        assert Severity.HIGH
        assert Severity.CRITICAL

    def test_has_exactly_four_levels(self):
        assert len(Severity) == 4

    def test_is_string_compatible(self):
        assert Severity.LOW == "LOW"
        assert Severity.CRITICAL == "CRITICAL"


class TestIncidentStatus:

    def test_has_all_required_values(self):
        assert IncidentStatus.OPEN
        assert IncidentStatus.ASSIGNED
        assert IncidentStatus.IN_PROGRESS
        assert IncidentStatus.RESOLVED
        assert IncidentStatus.CLOSED

    def test_has_exactly_five_statuses(self):
        assert len(IncidentStatus) == 5

    def test_is_string_compatible(self):
        assert IncidentStatus.OPEN == "OPEN"
        assert IncidentStatus.IN_PROGRESS == "IN_PROGRESS"


class TestTaskStatus:

    def test_has_all_required_values(self):
        assert TaskStatus.OPEN
        assert TaskStatus.IN_PROGRESS
        assert TaskStatus.DONE

    def test_has_exactly_three_statuses(self):
        assert len(TaskStatus) == 3

    def test_is_string_compatible(self):
        assert TaskStatus.OPEN == "OPEN"
        assert TaskStatus.DONE == "DONE"


class TestEventType:

    def test_has_all_required_values(self):
        assert EventType.INCIDENT_CREATED
        assert EventType.INCIDENT_ASSIGNED
        assert EventType.INCIDENT_STATUS_CHANGED
        assert EventType.TASK_CREATED
        assert EventType.TASK_DONE

    def test_has_exactly_five_events(self):
        assert len(EventType) == 5

    def test_is_string_compatible(self):
        assert EventType.INCIDENT_CREATED == "INCIDENT_CREATED"
        assert EventType.TASK_DONE == "TASK_DONE"


class TestNotificationStatus:

    def test_has_all_required_values(self):
        assert NotificationStatus.PENDING
        assert NotificationStatus.SENT
        assert NotificationStatus.FAILED

    def test_has_exactly_three_statuses(self):
        assert len(NotificationStatus) == 3

    def test_is_string_compatible(self):
        assert NotificationStatus.PENDING == "PENDING"
        assert NotificationStatus.FAILED == "FAILED"


class TestNotificationChannel:

    def test_has_all_required_values(self):
        assert NotificationChannel.EMAIL
        assert NotificationChannel.IN_APP

    def test_has_exactly_two_channels(self):
        assert len(NotificationChannel) == 2

    def test_is_string_compatible(self):
        assert NotificationChannel.EMAIL == "EMAIL"
        assert NotificationChannel.IN_APP == "IN_APP"


class TestEnumSerializability:

    def test_all_enums_are_strings(self):
        for enum_class in [
            Role, Severity, IncidentStatus,
            TaskStatus, EventType, NotificationStatus,
            NotificationChannel,
        ]:
            for member in enum_class:
                assert isinstance(member, str), (
                    f"{enum_class.__name__}.{member.name} is not a str subclass"
                )

    def test_constructible_from_string_value(self):
        assert Role("ADMIN") == Role.ADMIN
        assert IncidentStatus("IN_PROGRESS") == IncidentStatus.IN_PROGRESS
        assert NotificationChannel("EMAIL") == NotificationChannel.EMAIL

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            Role("SUPERADMIN")
        with pytest.raises(ValueError):
            IncidentStatus("DELETED")