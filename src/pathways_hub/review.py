"""Auditable research review event machine.

This is a deterministic integrity checksum chain, NOT a cryptographic signature
or proof of actor identity. Fixture identities are synthetic, never external collaborators.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json


class ReviewError(ValueError):
    pass


ACTIONS = {
    "SUBMIT", "SCHEMA_ACCEPT", "REQUEST_REVIEW", "REQUEST_CHANGES",
    "RESUBMIT", "APPROVE", "RELEASE", "WITHDRAW",
}


def digest(document):
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return sha256(encoded).hexdigest()


def validate_timestamp(value):
    if not isinstance(value, str) or not value:
        raise ReviewError("Event must declare its actual RFC3339 timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ReviewError("Invalid event timestamp") from e
    if dt.tzinfo is None:
        raise ReviewError("Event timestamp must include UTC offset")
    return dt.astimezone(timezone.utc)


def state_transition(state, event, *, submitter, evidence_level, permissions):
    action, actor, role = event["action"], event["actor"], event["role"]
    if action not in ACTIONS:
        raise ReviewError(f"Unknown review action {action}")
    if action in {"SUBMIT", "RESUBMIT", "WITHDRAW"} and actor != submitter:
        raise ReviewError("Only declared submitter may submit, resubmit or withdraw")
    if action in {"SCHEMA_ACCEPT", "REQUEST_REVIEW"} and role not in ("system", "coordinator"):
        raise ReviewError("Only the system or coordinator may advance intake")
    if action in {"REQUEST_CHANGES", "APPROVE"}:
        if role != "reviewer" or actor == submitter:
            raise ReviewError("Review requires distinct reviewer identity")
        if not event.get("evidence_ref"):
            raise ReviewError("A review decision must cite a concrete source artifact")
    if action == "RELEASE":
        if role != "publisher" or actor == submitter:
            raise ReviewError("Publisher must be distinct from submitter")
        if permissions != "PUBLIC_DERIVED":
            raise ReviewError("Release requires explicit PUBLIC_DERIVED permission")
        if evidence_level == "SIMULATION_ONLY":
            raise ReviewError("Synthetic review cannot authorize real publication")

    transitions = {
        ("DRAFT", "SUBMIT"): "SUBMITTED",
        ("SUBMITTED", "SCHEMA_ACCEPT"): "ACCEPTED_SCHEMA_ONLY",
        ("ACCEPTED_SCHEMA_ONLY", "REQUEST_REVIEW"): "IN_REVIEW",
        ("IN_REVIEW", "REQUEST_CHANGES"): "CHANGES_REQUESTED",
        ("CHANGES_REQUESTED", "RESUBMIT"): "SUBMITTED",
        ("IN_REVIEW", "APPROVE"): "SIMULATED_APPROVAL_ONLY" if evidence_level == "SIMULATION_ONLY" else "HUMAN_APPROVED_REVIEW",
        ("HUMAN_APPROVED_REVIEW", "RELEASE"): "RELEASED",
    }
    if action == "WITHDRAW" and state in ("SUBMITTED", "ACCEPTED_SCHEMA_ONLY", "IN_REVIEW", "CHANGES_REQUESTED", "HUMAN_APPROVED_REVIEW"):
        return "WITHDRAWN"
    if (state, action) not in transitions:
        raise ReviewError(f"Invalid state transition {state} + {action}")
    return transitions[(state, action)]


def validate_review_ledger(document: dict) -> dict:
    """Recompute entire chain; no timestamps/roles can be retroactively reinterpreted."""
    if not isinstance(document, dict):
        raise ReviewError("Ledger must be JSON object")
    evidence_level = document.get("evidence_level")
    if evidence_level not in ("SIMULATION_ONLY", "EXTERNALLY_EXERCISED"):
        raise ReviewError("Evidence level must be explicitly declared")
    if evidence_level == "EXTERNALLY_EXERCISED" and not document.get("external_verification_ref"):
        raise ReviewError("External participation requires separately reviewed verification evidence")
    submitter = document.get("submitter")
    if not isinstance(submitter, str) or not submitter:
        raise ReviewError("Declared submitter required")
    events = document.get("events")
    if not isinstance(events, list) or not events:
        raise ReviewError("At least one event required")
    state, previous, last_dt = "DRAFT", "GENESIS", None
    seen_ids = set()
    history = []
    for index, event in enumerate(events, start=1):
        required = ("event_id", "actor", "role", "timestamp", "action", "prev_sha256", "sha256")
        if not isinstance(event, dict) or any(k not in event for k in required):
            raise ReviewError(f"Event {index} missing required fields")
        if event["event_id"] in seen_ids:
            raise ReviewError("Duplicate event ID")
        seen_ids.add(event["event_id"])
        dt = validate_timestamp(event["timestamp"])
        if last_dt is not None and dt < last_dt:
            raise ReviewError("Events out of temporal order")
        last_dt = dt
        if event["prev_sha256"] != previous:
            raise ReviewError(f"Event {index} hash chain broken")
        unsigned = {k: v for k, v in event.items() if k != "sha256"}
        expected = digest(unsigned)
        if expected != event["sha256"]:
            raise ReviewError(f"Event {index} content checksum mismatch")
        state = state_transition(state, event, submitter=submitter,
                                 evidence_level=evidence_level,
                                 permissions=document.get("publication_permission"))
        previous = expected
        history.append({"event_id": event["event_id"], "action": event["action"],
                        "state": state, "checksum": previous})
    return {"status": "VALID_INTEGRITY_CHAIN", "evidence_level": evidence_level,
            "last_state": state, "event_count": len(events), "last_sha256": previous,
            "history": history, "warning": "Checksums are not signatures or proof of real participation."}


def add_event(document, *, event_id, timestamp, actor, role, action, evidence_ref=None):
    """Pure deterministic helper for fixtures; recomputes chain without inserting clock values."""
    output = json.loads(json.dumps(document))
    events = output.setdefault("events", [])
    unsigned = {"event_id": event_id, "timestamp": timestamp,
                "actor": actor, "role": role, "action": action,
                "prev_sha256": events[-1]["sha256"] if events else "GENESIS"}
    if evidence_ref is not None:
        unsigned["evidence_ref"] = evidence_ref
    unsigned["sha256"] = digest(unsigned)
    events.append(unsigned)
    # Invalid transitions are not materialized as accepted documents
    validate_review_ledger(output)
    return output


def run_review(path, destination):
    source = json.loads(Path(path).read_text(encoding="utf-8"))
    report = validate_review_ledger(source)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
