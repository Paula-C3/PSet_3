import pytest               #type:ignore

from backend.domain.entities import Incident
from backend.domain.enums import IncidentStatus, Severity
from backend.domain.state import (
    AssignedState,
    ClosedState,
    InProgressState,
    InvalidTransitionError,
    OpenState,
    ResolvedState,
    state_for,
)


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def open_incident():
    return Incident(
        title="Network outage",
        description="Packet loss above 30% on us-east-1",
        severity=Severity.CRITICAL,
        created_by="user-001",
    )


@pytest.fixture
def assigned_incident(open_incident):
    open_incident.assign("user-002")
    return open_incident


@pytest.fixture
def in_progress_incident(assigned_incident):
    assigned_incident.start_progress()
    return assigned_incident


@pytest.fixture
def resolved_incident(in_progress_incident):
    in_progress_incident.resolve()
    return in_progress_incident


@pytest.fixture
def closed_incident(resolved_incident):
    resolved_incident.close()
    return resolved_incident


# ── state_for() resolver ──────────────────────────────────────────────

class TestStateFor:

    def test_open_status_returns_open_state(self):
        assert isinstance(state_for(IncidentStatus.OPEN), OpenState)

    def test_assigned_status_returns_assigned_state(self):
        assert isinstance(state_for(IncidentStatus.ASSIGNED), AssignedState)

    def test_in_progress_status_returns_in_progress_state(self):
        assert isinstance(state_for(IncidentStatus.IN_PROGRESS), InProgressState)

    def test_resolved_status_returns_resolved_state(self):
        assert isinstance(state_for(IncidentStatus.RESOLVED), ResolvedState)

    def test_closed_status_returns_closed_state(self):
        assert isinstance(state_for(IncidentStatus.CLOSED), ClosedState)

    def test_incident_loaded_from_db_gets_correct_state(self):
        # Simulates P3 constructing an Incident from an ORM model
        # where status is already set to a non-default value.
        incident = Incident(
            title="T",
            description="D",
            severity=Severity.LOW,
            created_by="u1",
            status=IncidentStatus.IN_PROGRESS,
        )
        assert isinstance(incident._state, InProgressState)


# ── OpenState transitions ─────────────────────────────────────────────

class TestOpenState:

    def test_assign_sets_assignee(self, open_incident):
        open_incident.assign("user-002")
        assert open_incident.assigned_to == "user-002"

    def test_assign_transitions_to_assigned(self, open_incident):
        open_incident.assign("user-002")
        assert open_incident.status == IncidentStatus.ASSIGNED
        assert isinstance(open_incident._state, AssignedState)

    def test_start_progress_raises(self, open_incident):
        with pytest.raises(InvalidTransitionError):
            open_incident.start_progress()

    def test_resolve_raises(self, open_incident):
        with pytest.raises(InvalidTransitionError):
            open_incident.resolve()

    def test_close_raises(self, open_incident):
        with pytest.raises(InvalidTransitionError):
            open_incident.close()


# ── AssignedState transitions ─────────────────────────────────────────

class TestAssignedState:

    def test_start_progress_transitions_correctly(self, assigned_incident):
        assigned_incident.start_progress()
        assert assigned_incident.status == IncidentStatus.IN_PROGRESS
        assert isinstance(assigned_incident._state, InProgressState)

    def test_reassign_updates_assignee_without_status_change(self, assigned_incident):
        assigned_incident.assign("user-999")
        assert assigned_incident.assigned_to == "user-999"
        assert assigned_incident.status == IncidentStatus.ASSIGNED

    def test_reassign_keeps_assigned_state(self, assigned_incident):
        assigned_incident.assign("user-999")
        assert isinstance(assigned_incident._state, AssignedState)

    def test_resolve_raises(self, assigned_incident):
        with pytest.raises(InvalidTransitionError):
            assigned_incident.resolve()

    def test_close_raises(self, assigned_incident):
        with pytest.raises(InvalidTransitionError):
            assigned_incident.close()


# ── InProgressState transitions ───────────────────────────────────────

class TestInProgressState:

    def test_resolve_transitions_correctly(self, in_progress_incident):
        in_progress_incident.resolve()
        assert in_progress_incident.status == IncidentStatus.RESOLVED
        assert isinstance(in_progress_incident._state, ResolvedState)

    def test_reassign_updates_assignee_without_status_change(self, in_progress_incident):
        in_progress_incident.assign("user-999")
        assert in_progress_incident.assigned_to == "user-999"
        assert in_progress_incident.status == IncidentStatus.IN_PROGRESS

    def test_reassign_keeps_in_progress_state(self, in_progress_incident):
        in_progress_incident.assign("user-999")
        assert isinstance(in_progress_incident._state, InProgressState)

    def test_start_progress_raises(self, in_progress_incident):
        with pytest.raises(InvalidTransitionError):
            in_progress_incident.start_progress()

    def test_close_raises(self, in_progress_incident):
        with pytest.raises(InvalidTransitionError):
            in_progress_incident.close()


# ── ResolvedState transitions ─────────────────────────────────────────

class TestResolvedState:

    def test_close_transitions_correctly(self, resolved_incident):
        resolved_incident.close()
        assert resolved_incident.status == IncidentStatus.CLOSED
        assert isinstance(resolved_incident._state, ClosedState)

    def test_assign_raises(self, resolved_incident):
        with pytest.raises(InvalidTransitionError):
            resolved_incident.assign("user-999")

    def test_start_progress_raises(self, resolved_incident):
        with pytest.raises(InvalidTransitionError):
            resolved_incident.start_progress()

    def test_resolve_raises(self, resolved_incident):
        with pytest.raises(InvalidTransitionError):
            resolved_incident.resolve()


# ── ClosedState transitions ───────────────────────────────────────────

class TestClosedState:

    def test_assign_raises(self, closed_incident):
        with pytest.raises(InvalidTransitionError):
            closed_incident.assign("user-999")

    def test_start_progress_raises(self, closed_incident):
        with pytest.raises(InvalidTransitionError):
            closed_incident.start_progress()

    def test_resolve_raises(self, closed_incident):
        with pytest.raises(InvalidTransitionError):
            closed_incident.resolve()

    def test_close_raises(self, closed_incident):
        with pytest.raises(InvalidTransitionError):
            closed_incident.close()


# ── Full lifecycle ────────────────────────────────────────────────────

class TestFullLifecycle:

    def test_happy_path_open_to_closed(self, open_incident):
        open_incident.assign("user-002")
        open_incident.start_progress()
        open_incident.resolve()
        open_incident.close()
        assert open_incident.status == IncidentStatus.CLOSED

    def test_error_message_contains_action_and_state(self, open_incident):
        with pytest.raises(InvalidTransitionError, match="start_progress"):
            open_incident.start_progress()

    def test_state_object_updates_at_each_transition(self, open_incident):
        assert isinstance(open_incident._state, OpenState)
        open_incident.assign("u1")
        assert isinstance(open_incident._state, AssignedState)
        open_incident.start_progress()
        assert isinstance(open_incident._state, InProgressState)
        open_incident.resolve()
        assert isinstance(open_incident._state, ResolvedState)
        open_incident.close()
        assert isinstance(open_incident._state, ClosedState)