"""Deterministic, fail-closed intake and source-release integrity checks."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

FIELDS = ("model", "scenario", "region", "variable", "unit", "year", "value")
RELEASE_FIELDS = ("schema_version", "release_id", "source_commit", "provenance_type",
                  "metric_id", "identifiability_level", "publication_permission", "dataset_sha256")


def read_json(filename):
    return json.loads(Path(filename).read_text(encoding="utf-8"))


def validate_submission(doc, protocol, source="submission"):
    errors = []
    def err(code, detail):
        errors.append({"submission": source, "severity": "ERROR", "code": code, "detail": detail})
    if doc.get("provenance_type") != "SYNTHETIC_TEST_ONLY":
        err("PROVENANCE_MISSING", "Demo intake requires an explicitly synthetic data source")
    if doc.get("protocol_version") != protocol["protocol_version"]:
        err("PROTOCOL_VERSION_MISMATCH", "Protocol version mismatch")
    records = doc.get("records")
    if not isinstance(records, list) or not records:
        err("NO_RECORDS", "Empty or invalid records array")
        return {"submission": source, "status": "REJECTED", "errors": errors, "observations": 0}
    seen = set()
    for i, item in enumerate(records, 1):
        if not isinstance(item, dict) or not all(k in item for k in FIELDS):
            err("INCOMPLETE_RECORD", f"Record {i} lacks required IAMC fields")
            continue
        key = tuple(str(item[k]) for k in FIELDS[:-1])
        if key in seen:
            err("DUPLICATE_RECORD", f"Record {i} duplicates IAMC observation key")
        seen.add(key)
        if (item["model"], item["scenario"]) != (doc.get("model"), doc.get("scenario")):
            err("MIXED_IDENTITY", f"Record {i} does not match submission identity")
        if item["region"] not in protocol["regions"]:
            err("REGION_MISMATCH", f"Record {i}: unknown region")
        if item["variable"] not in protocol["variables"]:
            err("UNEXPECTED_VARIABLE", f"Record {i}: unknown variable")
        elif item["unit"] != protocol["units"][item["variable"]]:
            err("UNIT_MISMATCH", f"Record {i}: incompatible unit; not silently converted")
        v = item["value"]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            err("INVALID_VALUE", f"Record {i}: non-numeric or non-finite value")
    for reg in protocol["regions"]:
        for var in protocol["variables"]:
            unit = protocol["units"][var]
            for year in protocol["years"]:
                key = (str(doc.get("model")), str(doc.get("scenario")), str(reg), str(var), str(unit), str(year))
                if key not in seen:
                    err("REQUIRED_OBSERVATION_MISSING", f"Missing {var} {year} {reg}")
    return {"submission": source, "status": "REJECTED" if errors else "ACCEPTED_SCHEMA_ONLY",
            "errors": errors, "observations": len(records), "provenance": doc.get("provenance_type")}


def validate_release(manifest, raw_artifact=None):
    """Check declared immutable ResidualPathways scientific artifact against its bytes."""
    problems = []
    for field in RELEASE_FIELDS:
        if not manifest.get(field):
            problems.append(f"MISSING_FIELD:{field}")
    if manifest.get("schema_version") != "1.0.0":
        problems.append("SCHEMA_VERSION_MISMATCH")
    if manifest.get("publication_permission") not in ("DERIVED_ANALYSIS_ONLY", "PUBLIC_DERIVED", "NO_REHOST", "SYNTHETIC_TEST_ONLY"):
        problems.append("PUBLICATION_PERMISSION_NOT_REVIEWED")
    if manifest.get("provenance_type") not in ("PUBLISHED_PUBLIC_TUTORIAL", "PUBLISHED_RESEARCH", "SYNTHETIC_TEST_ONLY"):
        problems.append("UNKNOWN_PROVENANCE")
    h = manifest.get("dataset_sha256", "")
    if len(str(h)) != 64 or any(x not in "0123456789abcdef" for x in str(h)):
        problems.append("INVALID_ARTIFACT_HASH")
    if raw_artifact is None:
        problems.append("MISSING_ARTIFACT")
    elif hashlib.sha256(raw_artifact).hexdigest() != h:
        problems.append("HASH_MISMATCH")
    level = manifest.get("identifiability_level")
    if level not in ("I0", "I1", "I2", "I3"):
        problems.append("UNKNOWN_IDENTIFIABILITY")
    if level == "I3" and manifest.get("scientific_status") != "I3_VERIFIED":
        problems.append("I3_NOT_VERIFIED")
    if problems:
        return {"status": "BLOCKED", "problems": sorted(set(problems))}
    return {"status": "READY_SCIENTIFIC_CLAIMS" if level == "I3" else "READY_COVERAGE_ONLY",
            "release_id": manifest["release_id"], "source_commit": manifest["source_commit"],
            "identifiability_level": level,
            "disclaimer": "Automated contract acceptance is not scientific peer review."}


def write_report(submissions, protocol, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    errors = [e for x in submissions for e in x["errors"]]
    statuses = dict(Counter(x["status"] for x in submissions))
    result = {"evidence_level": "SIMULATION_ONLY", "protocol_version": protocol["protocol_version"],
              "submissions": submissions, "status_counts": statuses, "issue_count": len(errors)}
    (directory / "status.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    with (directory / "issues.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=("submission", "severity", "code", "detail"))
        w.writeheader()
        w.writerows(errors)
    lines = ["# Simulated scenario intake briefing", "",
             "**SYNTHETIC_TEST_ONLY — not a real cross-team coordination exercise**", "",
             f"Protocol {protocol['protocol_version']}: {len(submissions)} test submissions, "
             f"{statuses.get('ACCEPTED_SCHEMA_ONLY', 0)} schema accepted, "
             f"{statuses.get('REJECTED', 0)} rejected, {len(errors)} reported issues.", "",
             "## Intake decisions (automated; no scientific endorsement)"]
    lines += [f"- {x['submission']}: {x['status']}." for x in submissions]
    lines += ["", "## Corrections required"]
    lines += [f"- {e['submission']}: {e['code']} — {e['detail']}" for e in errors]
    lines += ["", "Scientific interpretation, publication and human approval remain outside this test.",
              "No real participants, decisions or institutional affiliation are claimed.", ""]
    (directory / "briefing.md").write_text("\n".join(lines))
    return result
