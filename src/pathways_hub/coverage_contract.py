"""Hash-pinned, fail-closed intake of AR6 coverage-only reporting aggregates.

This separate contract NEVER maps REVIEW_PENDING to I0, I1, I2 or I3.
Presence of carbon-related IAMC variables is not a disjoint carbon ledger.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re

SCHEMA = "residualpathways.coverage-only.v1"
TOP_FIELDS = {"schema", "version", "scope", "evidence", "science_review_state",
              "i3_verified", "physical_accounting", "source_authentication",
              "metadata_concordance_status", "sha256", "metadata_sheet", "years",
              "categories", "variables", "cohort_size", "weighting", "records", "limitations"}
FIELDS = {"category", "year", "variable", "denominator", "reporting",
          "model_labels", "scenario_fraction", "model_label_balanced_fraction", "units"}
CATEGORIES = [f"C{i}" for i in range(1, 9)]
YEARS = [2030, 2050, 2070, 2100]


class CoverageContractError(ValueError):
    pass


def _unique_pairs(items):
    result = {}
    for name, value in items:
        if name in result:
            raise CoverageContractError("Duplicate JSON key rejected")
        result[name] = value
    return result


def _valid_digest(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def receive(raw_artifact, checksum_text, *, expected_sha256):
    try:
        if not isinstance(raw_artifact, bytes) or not raw_artifact or len(raw_artifact) > 524288:
            raise CoverageContractError("Invalid coverage-only artifact bytes")
        if not _valid_digest(expected_sha256):
            raise CoverageContractError("Out-of-band SHA-256 pin required")
        sidecar = checksum_text.decode("ascii") if isinstance(checksum_text, bytes) else checksum_text
        if not isinstance(sidecar, str):
            raise CoverageContractError("Invalid SHA sidecar")
        parts = sidecar.strip().split()
        if len(parts) != 2 or parts[1] != "coverage_release.json" or not _valid_digest(parts[0]):
            raise CoverageContractError("Malformed or misnamed SHA-256 sidecar")
        actual = sha256(raw_artifact).hexdigest()
        if actual != expected_sha256 or actual != parts[0]:
            raise CoverageContractError("Artifact does not match pinned and sidecar SHA-256")
        try:
            doc = json.loads(raw_artifact.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except (UnicodeError, ValueError) as e:
            raise CoverageContractError("Malformed JSON artifact") from e
        if not isinstance(doc, dict) or set(doc) != TOP_FIELDS or doc.get("schema") != SCHEMA:
            raise CoverageContractError("Unsupported scientific release schema or top-level field")
        if (doc["version"] != "0.1.0-candidate"
                or doc["scope"] != "World / climate-vetted C1-C8 / four years"
                or doc["metadata_sheet"] != "meta_Ch3vetted_withclimate"
                or doc["source_authentication"] != "LOCAL_FINGERPRINT_ONLY_PUBLISHER_RECEIPT_NOT_INDEPENDENTLY_VERIFIED"
                or doc["metadata_concordance_status"] not in ("DIFFERENCES_RECORDED", "EQUIVALENT_NORMALIZED_CELLS")):
            raise CoverageContractError("Invalid release scope, version, or provenance")
        if (type(doc["weighting"]) is not dict or set(doc["weighting"]) != {"scenario", "model_label_balanced"}
                or type(doc["limitations"]) is not list or not doc["limitations"]):
            raise CoverageContractError("Missing source limitations")
        if (doc.get("science_review_state") != "REVIEW_PENDING"
                or doc.get("i3_verified") != 0 or type(doc["i3_verified"]) is not int
                or doc.get("physical_accounting") != "NOT_ESTABLISHED"
                or doc.get("evidence") != "EXACT_VARIABLE_REPORTING_PRESENCE_ONLY"):
            raise CoverageContractError("Attempt to promote unreviewed coverage to scientific I3 evidence")
        if doc.get("years") != YEARS or doc.get("categories") != CATEGORIES:
            raise CoverageContractError("Unknown cohort dimensions")
        variables = doc.get("variables")
        if not isinstance(variables, list) or not variables or len(variables) != len(set(variables)):
            raise CoverageContractError("Invalid variable dimensions")
        if not all(isinstance(v, str) and v for v in variables):
            raise CoverageContractError("Variable label must be text")
        if not isinstance(doc.get("sha256"), dict) or set(doc["sha256"]) != {"world_csv", "metadata_xlsx"}:
            raise CoverageContractError("Source SHA-256 manifest missing")
        if not all(_valid_digest(d) for d in doc["sha256"].values()):
            raise CoverageContractError("Malformed source fingerprints")
        rows = doc.get("records")
        if not isinstance(rows, list) or len(rows) != len(YEARS) * len(CATEGORIES) * len(variables):
            raise CoverageContractError("Incomplete reporting coverage cross-product")
        observed, denominators = set(), {}
        for row in rows:
            if not isinstance(row, dict) or set(row) != FIELDS:
                raise CoverageContractError("Unexpected record field, possibly identifying private input")
            key = (row["category"], row["year"], row["variable"])
            if key in observed or key[0] not in CATEGORIES or key[1] not in YEARS or key[2] not in variables:
                raise CoverageContractError("Duplicate or unsupported aggregation keys")
            observed.add(key)
            n, k, m = row["denominator"], row["reporting"], row["model_labels"]
            if any(type(x) is not int for x in (n, k, m)) or not (1 <= m <= n and 0 <= k <= n):
                raise CoverageContractError("Invalid reported counts")
            dk = key[:2]
            if dk in denominators and denominators[dk] != (n, m):
                raise CoverageContractError("Conflicting denominators")
            denominators[dk] = n, m
            s, b = row["scenario_fraction"], row["model_label_balanced_fraction"]
            if (type(s) not in (float, int) or type(b) not in (float, int)
                    or not math.isfinite(s) or not math.isfinite(b)
                    or not 0 <= s <= 1 or not 0 <= b <= 1 or abs(s - k/n) > 1e-9):
                raise CoverageContractError("Invalid aggregate fractions")
            if not isinstance(row["units"], list) or not all(isinstance(u, str) for u in row["units"]):
                raise CoverageContractError("Unexpected units data")
        if len(observed) != len(CATEGORIES) * len(YEARS) * len(variables):
            raise CoverageContractError("Incomplete coverage indices")
        total = {year: sum(denominators[(cat, year)][0] for cat in CATEGORIES) for year in YEARS}
        if (len(set(total.values())) != 1 or type(doc.get("cohort_size")) is not int
                or doc["cohort_size"] != total[2050]):
            raise CoverageContractError("Source cohort denominator mismatch")
    except (CoverageContractError, KeyError, TypeError, OverflowError, ZeroDivisionError) as e:
        return {
            "status": "BLOCKED", "problems": [str(e)],
            "scientifically_reviewed": False, "identifiability": "NOT_ASSESSED",
            "verified_i3": 0,
        }
    return {
        "status": "ACCEPTED_COVERAGE_ONLY_UNREVIEWED",
        "artifact_sha256": actual,
        "source_sha256": doc["sha256"],
        "cohort_size": total[2050],
        "years": YEARS,
        "categories": CATEGORIES,
        "reported_variables": len(variables),
        "scientifically_reviewed": False,
        "identifiability": "NOT_ASSESSED",
        "verified_i3": 0,
        "interpretation": "Exact-name presence counts accepted by byte integrity; no physical carbon partition, reviewer approval, or independent model-family weighting.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--sha-file", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs/coverage_contract/report.json"))
    args = parser.parse_args()
    try:
        result = receive(args.artifact.read_bytes(), args.sha_file.read_text(),
                         expected_sha256=args.expected_sha256)
    except (OSError, UnicodeError) as e:
        result = {"status": "BLOCKED", "problems": [str(e)],
                  "scientifically_reviewed": False, "identifiability": "NOT_ASSESSED", "verified_i3": 0}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    if result["status"] == "BLOCKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
