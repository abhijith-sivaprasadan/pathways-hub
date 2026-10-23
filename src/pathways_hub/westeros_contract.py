"""Validate a *separate* MESSAGEix Westeros evidence handoff.

This contract accepts author-attested local solve metadata with byte integrity
and strict semantics. It never treats local metadata as independently witnessed
execution, an IAMC I0 release, an AR6 result or scientific endorsement.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import re

BUNDLE_SCHEMA = "pathways-handoff.westeros.v1"
EVIDENCE_SCHEMA = "residualpathways.westeros.evidence.v1"
ATTESTATION = "AUTHOR_REPORTED_LOCAL_EXECUTION_NOT_INDEPENDENTLY_VERIFIED"
UPSTREAM_COMMIT = "2d521407a430a08de997a771e7b38d88f7e7d2b6"
SCOPE = "EDUCATIONAL_MESSAGEIX_GAMS_NOT_AR6"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
RUN_ID = re.compile(r"[0-9]{8}T[0-9]{6}Z_[0-9a-f]{8}\Z")
INDEX_KEYS = {
    "schema_version", "artifact_name", "artifact_sha256", "artifact_bytes",
    "publication_scope", "attestation",
}
ARTIFACT_KEYS = {
    "schema_version", "provenance", "source_project", "source_run_id",
    "source_run_status", "scientific_scope", "model", "upstream_commit",
    "upstream_release", "message_ix_version", "ixmp_version", "scenarios",
}
SCENARIO_KEYS = {
    "scenario", "version", "has_solution", "objective_native",
    "notebook_source_sha256",
}


class WesterosContractError(ValueError):
    pass


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise WesterosContractError("Duplicate JSON key")
        out[key] = value
    return out


def _require(ok, reason):
    if not ok:
        raise WesterosContractError(reason)


def _exact_keys(doc, expected, description):
    _require(type(doc) is dict and set(doc) == expected,
             f"Unexpected/missing fields in {description}")


def _digest(x):
    return type(x) is str and HEX64.fullmatch(x) is not None


def _check_artifact(artifact):
    _exact_keys(artifact, ARTIFACT_KEYS, "Westeros artifact")
    for key, value in {
        "schema_version": EVIDENCE_SCHEMA,
        "provenance": ATTESTATION,
        "source_project": "residual-pathways",
        "source_run_status": "ACTUAL_MESSAGEIX_GAMS_SOLVED",
        "scientific_scope": SCOPE,
        "model": "Westeros Electrified",
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_release": "v3.11.1",
        "message_ix_version": "3.11.1",
        "ixmp_version": "3.11.1",
    }.items():
        _require(artifact[key] == value, f"Unexpected {key}")
    run_id = artifact["source_run_id"]
    _require(type(run_id) is str and RUN_ID.fullmatch(run_id), "Invalid source_run_id")
    rows = artifact["scenarios"]
    _require(type(rows) is list and len(rows) == 2, "Expected exactly two scenarios")
    objectives = {}
    for row, expected_stage in zip(rows, ("baseline", "emission_bound")):
        _exact_keys(row, SCENARIO_KEYS, "scenario record")
        _require(row["scenario"] == expected_stage, "Unexpected or reordered scenario")
        _require(row["has_solution"] is True, "Scenario does not declare saved solution")
        _require(type(row["version"]) is int and row["version"] >= 1, "Invalid scenario version")
        _require(_digest(row["notebook_source_sha256"]), "Invalid notebook SHA-256")
        v = row["objective_native"]
        _require(type(v) in (float, int) and math.isfinite(v), "Invalid objective level")
        objectives[expected_stage] = v
    return objectives


def validate_westeros_bundle(index, raw_artifact, *, expected_sha256=None):
    """Never claim actual independent solve, even on a valid SHA-256 handoff."""
    try:
        _exact_keys(index, INDEX_KEYS, "handoff index")
        _require(index["schema_version"] == BUNDLE_SCHEMA, "Unsupported bundle schema")
        _require(index["artifact_name"] == "westeros_evidence.json", "Unexpected artifact name")
        _require(index["publication_scope"] == "SANITIZED_DERIVED_METADATA_ONLY",
                 "Unsupported publication scope")
        _require(index["attestation"] == ATTESTATION, "Unacceptable attestation claim")
        digest = index["artifact_sha256"]
        _require(_digest(digest), "Invalid manifest artifact hash")
        _require(type(index["artifact_bytes"]) is int and 0 < index["artifact_bytes"] <= 65536,
                 "Invalid artifact size declaration")
        _require(type(raw_artifact) is bytes and len(raw_artifact) == index["artifact_bytes"],
                 "Artifact bytes missing or length mismatch")
        _require(sha256(raw_artifact).hexdigest() == digest, "Artifact SHA-256 mismatch")
        if expected_sha256 is not None:
            _require(_digest(expected_sha256) and expected_sha256 == digest,
                     "Out-of-band expected SHA-256 mismatch")
        try:
            artifact = json.loads(raw_artifact.decode("utf-8"), object_pairs_hook=_unique_object)
        except (UnicodeError, ValueError) as exc:
            raise WesterosContractError("Malformed artifact JSON") from exc
        objectives = _check_artifact(artifact)
    except (WesterosContractError, TypeError, OverflowError) as exc:
        return {
            "status": "BLOCKED",
            "problems": [str(exc)],
            "independently_reproduced": False,
            "scientific_scope": SCOPE,
        }
    baseline = objectives["baseline"]
    bounded = objectives["emission_bound"]
    difference = bounded - baseline
    change_pct = difference / baseline * 100 if baseline != 0 else None
    if not math.isfinite(difference) or (change_pct is not None and not math.isfinite(change_pct)):
        return {"status": "BLOCKED", "problems": ["Non-finite derived comparison"],
                "independently_reproduced": False, "scientific_scope": SCOPE}
    return {
        "status": "ACCEPTED_AUTHOR_REPORTED_LOCAL",
        "integrity": "BYTE_HASH_MATCH_AND_SCHEMA_CHECKED",
        "attestation": ATTESTATION,
        "source_run_id": artifact["source_run_id"],
        "upstream_commit": UPSTREAM_COMMIT,
        "artifact_sha256": digest,
        "scientific_scope": SCOPE,
        "scenarios": objectives,
        "objective_difference_native": difference,
        "objective_change_percent": change_pct,
        "independently_reproduced": False,
        "scientifically_reviewed": False,
        "warning": "Matching hashes on two files do not prove authorship or GAMS execution. The source solver did not run in PathwaysHub.",
    }
