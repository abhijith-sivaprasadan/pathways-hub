"""Synthetic hash-pinned coverage-only receiver; no AR6 scenario values."""
from hashlib import sha256
import json

import pytest
from pathways_hub.coverage_contract import receive, YEARS, CATEGORIES


def bundle():
    variables = ["Emissions|CO2", "Carbon Sequestration|Direct Air Capture"]
    rows = []
    for year in YEARS:
        for cat in CATEGORIES:
            for name in variables:
                rows.append({"category": cat, "year": year, "variable": name,
                             "denominator": 3, "reporting": 2, "model_labels": 2,
                             "scenario_fraction": 2/3, "model_label_balanced_fraction": 0.75,
                             "units": ["Mt CO2/yr"]})
    return {
        "schema": "residualpathways.coverage-only.v1",
        "science_review_state": "REVIEW_PENDING", "i3_verified": 0,
        "physical_accounting": "NOT_ESTABLISHED",
        "evidence": "EXACT_VARIABLE_REPORTING_PRESENCE_ONLY",
        "years": YEARS, "categories": CATEGORIES, "variables": variables,
        "sha256": {"world_csv": "a"*64, "metadata_xlsx": "b"*64},
        "cohort_size": 24, "records": rows,
    }


def run(doc, *, corrupt=False, bad_pin=False):
    raw = (json.dumps(doc, sort_keys=True) + "\n").encode()
    d = sha256(raw).hexdigest()
    sidecar = ("0"*64 if corrupt else d) + "  coverage_release.json\n"
    pin = ("f"*64 if bad_pin else d)
    return receive(raw, sidecar, expected_sha256=pin)


def test_accept_only_coverage_without_i0_or_i3_promotion():
    x = run(bundle())
    assert x["status"] == "ACCEPTED_COVERAGE_ONLY_UNREVIEWED"
    assert x["identifiability"] == "NOT_ASSESSED"
    assert x["verified_i3"] == 0
    assert x["scientifically_reviewed"] is False
    assert x["cohort_size"] == 24


@pytest.mark.parametrize("bad", ["sidecar", "pin", "gross", "i3", "unknown_private_field", "incomplete", "fraction", "denom"])
def test_contract_fails_closed(bad):
    doc = bundle()
    if bad == "sidecar":
        x = run(doc, corrupt=True)
    elif bad == "pin":
        x = run(doc, bad_pin=True)
    else:
        if bad == "gross": doc["physical_accounting"] = "RECONSTRUCTED"
        if bad == "i3": doc["i3_verified"] = 1
        if bad == "unknown_private_field": doc["records"][0]["Model"] = "private"
        if bad == "incomplete": doc["records"].pop()
        if bad == "fraction": doc["records"][0]["scenario_fraction"] = 1.0
        if bad == "denom": doc["records"][0]["denominator"] = 2
        x = run(doc)
    assert x["status"] == "BLOCKED"
    assert x["verified_i3"] == 0
    assert x["identifiability"] == "NOT_ASSESSED"


def test_duplicate_json_keys_blocked():
    raw = b'{"schema":"x","schema":"y"}'
    d = sha256(raw).hexdigest()
    x = receive(raw, d+"  coverage_release.json\n", expected_sha256=d)
    assert x["status"] == "BLOCKED"


def test_absent_frozen_input_not_accepted():
    x = receive(b"", "0"*64+"  coverage_release.json", expected_sha256="0"*64)
    assert x["status"] == "BLOCKED"
