"""Synthetic contract fixtures only; no GAMS execution in CI."""
import json
from hashlib import sha256

import pytest

from pathways_hub.westeros_contract import (
    ATTESTATION, SCOPE, UPSTREAM_COMMIT, validate_westeros_bundle,
)


def sample_artifact():
    return {
        "schema_version": "residualpathways.westeros.evidence.v1",
        "provenance": ATTESTATION,
        "source_project": "residual-pathways",
        "source_run_id": "20261023T230104Z_e182e730",
        "source_run_status": "ACTUAL_MESSAGEIX_GAMS_SOLVED",
        "scientific_scope": SCOPE,
        "model": "Westeros Electrified",
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_release": "v3.11.1",
        "message_ix_version": "3.11.1",
        "ixmp_version": "3.11.1",
        "scenarios": [
            {"scenario": "baseline", "has_solution": True, "version": 1,
             "objective_native": 159025.830480, "notebook_source_sha256": "a" * 64},
            {"scenario": "emission_bound", "has_solution": True, "version": 1,
             "objective_native": 191510.804279, "notebook_source_sha256": "b" * 64},
        ],
    }


def bundle(doc=None):
    raw = (json.dumps(sample_artifact() if doc is None else doc, sort_keys=True,
                      allow_nan=False) + "\n").encode("utf-8")
    index = {
        "schema_version": "pathways-handoff.westeros.v1",
        "artifact_name": "westeros_evidence.json",
        "artifact_sha256": sha256(raw).hexdigest(),
        "artifact_bytes": len(raw),
        "publication_scope": "SANITIZED_DERIVED_METADATA_ONLY",
        "attestation": ATTESTATION,
    }
    return index, raw


def test_synthetic_contract_only_claims_author_reported_local():
    index, raw = bundle()
    decision = validate_westeros_bundle(index, raw)
    assert decision["status"] == "ACCEPTED_AUTHOR_REPORTED_LOCAL"
    assert decision["integrity"] == "BYTE_HASH_MATCH_AND_SCHEMA_CHECKED"
    assert decision["independently_reproduced"] is False
    assert decision["scientifically_reviewed"] is False
    assert decision["scenarios"]["baseline"] == 159025.830480
    assert abs(decision["objective_change_percent"] - 20.43) < 0.02


def test_hash_mismatch_blocks():
    index, raw = bundle()
    assert validate_westeros_bundle(index, raw + b" ")["status"] == "BLOCKED"
    modified = bytearray(raw)
    modified[0] ^= 1
    assert validate_westeros_bundle(index, bytes(modified))["status"] == "BLOCKED"


def test_out_of_band_pinning():
    index, raw = bundle()
    assert validate_westeros_bundle(index, raw, expected_sha256=index["artifact_sha256"])["status"] == "ACCEPTED_AUTHOR_REPORTED_LOCAL"
    assert validate_westeros_bundle(index, raw, expected_sha256="0" * 64)["status"] == "BLOCKED"


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(provenance="CI_EXECUTED_GAMS"),
    lambda d: d.update(scientific_scope="AR6_WORLD_GROSS_CO2"),
    lambda d: d.update(upstream_commit="0" * 40),
    lambda d: d.update(extra_private_key="SECRET"),
    lambda d: d["scenarios"][0].update(has_solution=False),
    lambda d: d["scenarios"][1].update(objective_native="191510.8"),
    lambda d: d["scenarios"][1].update(objective_native=None),
    lambda d: d["scenarios"][0].update(notebook_source_sha256="broken"),
    lambda d: d["scenarios"].reverse(),
    lambda d: d["scenarios"].pop(),
    lambda d: d["scenarios"][0].update(version=True),
    lambda d: d["scenarios"][0].update(private_username="SECRET"),
])
def test_reject_invalid_or_overclaiming_artifacts(mutate):
    doc = sample_artifact()
    mutate(doc)
    index, raw = bundle(doc)
    assert validate_westeros_bundle(index, raw)["status"] == "BLOCKED"


def test_reject_nonfinite_even_with_matching_hash():
    doc = sample_artifact()
    doc["scenarios"][0]["objective_native"] = float("nan")
    raw = json.dumps(doc, allow_nan=True).encode()
    index, _ = bundle()
    index["artifact_sha256"] = sha256(raw).hexdigest()
    index["artifact_bytes"] = len(raw)
    assert validate_westeros_bundle(index, raw)["status"] == "BLOCKED"


def test_reject_duplicate_json_keys():
    index, raw = bundle()
    raw = raw.replace(b'"source_project": "residual-pathways"', b'"source_project": "residual-pathways", "source_project": "injected"')
    index["artifact_sha256"] = sha256(raw).hexdigest()
    index["artifact_bytes"] = len(raw)
    assert validate_westeros_bundle(index, raw)["status"] == "BLOCKED"


def test_reject_extra_bundle_keys_and_bool_size():
    index, raw = bundle()
    index["license_content"] = "SHOULD_NOT_BE_PRESENT"
    assert validate_westeros_bundle(index, raw)["status"] == "BLOCKED"
    index, raw = bundle()
    index["artifact_bytes"] = True
    assert validate_westeros_bundle(index, raw)["status"] == "BLOCKED"
