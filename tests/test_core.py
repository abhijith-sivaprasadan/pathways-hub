import hashlib
import json
from pathlib import Path
from pathways_hub.core import read_json, validate_submission, validate_release, write_report

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = read_json(ROOT / "protocols/v1.json")


def fixture(name):
    return read_json(ROOT / "fixtures" / f"{name}.json")


def test_good_fixture():
    result = validate_submission(fixture("team_a"), PROTOCOL)
    assert result["status"] == "ACCEPTED_SCHEMA_ONLY"


def test_incompatible_units_are_not_converted():
    result = validate_submission(fixture("team_b"), PROTOCOL)
    assert "UNIT_MISMATCH" in {e["code"] for e in result["errors"]}


def test_missing_year_not_zero_filled():
    result = validate_submission(fixture("team_c"), PROTOCOL)
    assert "REQUIRED_OBSERVATION_MISSING" in {e["code"] for e in result["errors"]}


def test_duplicate_fails():
    record = fixture("team_a")
    record["records"].append(record["records"][0])
    result = validate_submission(record, PROTOCOL)
    assert "DUPLICATE_RECORD" in {e["code"] for e in result["errors"]}


def test_cross_scenario_record_fails():
    record = fixture("team_a")
    record["records"][0]["scenario"] = "Other"
    result = validate_submission(record, PROTOCOL)
    assert "MIXED_IDENTITY" in {e["code"] for e in result["errors"]}


def test_nonfinite_fails():
    record = fixture("team_a")
    record["records"][0]["value"] = float("nan")
    result = validate_submission(record, PROTOCOL)
    assert "INVALID_VALUE" in {e["code"] for e in result["errors"]}


def test_reporting_with_error_registry(tmp_path):
    data = [validate_submission(fixture(n), PROTOCOL, n) for n in ("team_a", "team_b", "team_c")]
    report = write_report(data, PROTOCOL, tmp_path)
    assert report["evidence_level"] == "SIMULATION_ONLY"
    assert report["status_counts"] == {"ACCEPTED_SCHEMA_ONLY": 1, "REJECTED": 2}
    assert report["issue_count"] >= 2
    assert "SYNTHETIC_TEST_ONLY" in (tmp_path / "briefing.md").read_text()


def manifest(raw=b'{"ok":true}'):
    return {"schema_version":"1.0.0","release_id":"synthetic-v1","source_commit":"abc",
            "provenance_type":"SYNTHETIC_TEST_ONLY","metric_id":"coverage",
            "identifiability_level":"I0","publication_permission":"SYNTHETIC_TEST_ONLY",
            "scientific_status":"COVERAGE_AND_COMPARISON_ONLY",
            "dataset_sha256":hashlib.sha256(raw).hexdigest()}


def test_matching_release_is_coverage_only():
    raw = b'{"ok":true}'
    assert validate_release(manifest(raw), raw)["status"] == "READY_COVERAGE_ONLY"


def test_missing_source_bytes_fails():
    assert "MISSING_ARTIFACT" in validate_release(manifest())["problems"]


def test_source_hash_mismatch_fails():
    assert "HASH_MISMATCH" in validate_release(manifest(), b"modified")["problems"]


def test_unverified_i3_cannot_pass():
    m = manifest()
    m["identifiability_level"] = "I3"
    assert "I3_NOT_VERIFIED" in validate_release(m, b'{"ok":true}')["problems"]


def test_wrong_contract_version_fails():
    m = manifest()
    m["schema_version"] = "2.0.0"
    assert "SCHEMA_VERSION_MISMATCH" in validate_release(m, b'{"ok":true}')["problems"]


def test_unsupported_i3_source_artifact_fails_even_if_manifest_claims_verified():
    raw = b'{"accounting":{"verified_i3_records":[]}}'
    m = manifest(raw)
    m["identifiability_level"] = "I3"
    m["scientific_status"] = "I3_VERIFIED"
    assert "NO_I3_SOURCE_RECORDS" in validate_release(m, raw)["problems"]


def test_i3_provenance_fails_when_component_checks_missing():
    import json
    raw = json.dumps({"accounting": {"verified_i3_records": [
        {"semantics_pass": True, "source_precision_pass": True,
         "materiality_pass": True, "reconciliation_pass": True, "provenance_pass": False}
    ]}}).encode()
    m = manifest(raw)
    m["identifiability_level"] = "I3"
    m["scientific_status"] = "I3_VERIFIED"
    assert "I3_RECORD_GATE_FAILURE" in validate_release(m, raw)["problems"]
