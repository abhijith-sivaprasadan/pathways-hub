import json
from copy import deepcopy
import pytest
from pathways_hub.review import add_event, validate_review_ledger, ReviewError


def started():
    doc = {"evidence_level": "SIMULATION_ONLY", "publication_permission": "SYNTHETIC_TEST_ONLY",
           "submitter": "synthetic-author", "events": []}
    steps = [
        ("1", "synthetic-author", "submitter", "SUBMIT", None),
        ("2", "synthetic-system", "system", "SCHEMA_ACCEPT", None),
        ("3", "synthetic-coordinator", "coordinator", "REQUEST_REVIEW", None),
        ("4", "synthetic-reviewer", "reviewer", "APPROVE", "fixtures/team_a.json"),
    ]
    for i, actor, role, action, source in steps:
        doc = add_event(doc, event_id=i, actor=actor, role=role, action=action,
                        evidence_ref=source, timestamp=f"2026-10-23T10:0{i}:00Z")
    return doc


def test_synthetic_review_cannot_be_described_as_real():
    r = validate_review_ledger(started())
    assert r["last_state"] == "SIMULATED_APPROVAL_ONLY"
    assert r["event_count"] == 4


def test_tamper_detection():
    d = started()
    d["events"][0]["role"] = "publisher"
    with pytest.raises(ReviewError, match="checksum"):
        validate_review_ledger(d)


def test_missing_reviewer_evidence_fails():
    d = started()
    d["events"] = d["events"][:3]
    with pytest.raises(ReviewError, match="concrete source artifact"):
        add_event(d, event_id="4", actor="synthetic-reviewer", role="reviewer", action="APPROVE",
                  timestamp="2026-10-23T10:04:00Z")


def test_submitter_cannot_review_self():
    d = started()
    d["events"] = d["events"][:3]
    with pytest.raises(ReviewError, match="distinct reviewer"):
        add_event(d, event_id="4", actor="synthetic-author", role="reviewer", action="APPROVE",
                  evidence_ref="fixtures/team_a.json", timestamp="2026-10-23T10:04:00Z")


def test_synthetic_publishing_rejected():
    d = started()
    d["publication_permission"] = "PUBLIC_DERIVED"
    with pytest.raises(ReviewError, match="Synthetic review"):
        add_event(d, event_id="5", actor="synthetic-publisher", role="publisher", action="RELEASE",
                  timestamp="2026-10-23T10:05:00Z")


def test_order_and_hash_check():
    d = started()
    d["events"][1]["timestamp"] = "2026-10-22T10:00:00Z"
    with pytest.raises(ReviewError, match="temporal order"):
        validate_review_ledger(d)


def test_external_evidence_gate():
    d = started()
    d["evidence_level"] = "EXTERNALLY_EXERCISED"
    with pytest.raises(ReviewError, match="verification evidence"):
        validate_review_ledger(d)
