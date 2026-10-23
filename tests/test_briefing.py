import hashlib
import json
import pytest
from pathways_hub.briefing import make_briefing, BriefingError
from pathlib import Path

MILESTONES = json.loads((Path(__file__).parents[1] / "protocols/workstream_v3.json").read_text())


def data():
    return {"schema_version":"residualpathways.analysis.v1",
            "source":{"git_revision":"abc"},
            "accounting":{"i3_scenarios":0},
            "comparison":{"matched_rows":1,"cohort_models":["X"],"common_scenarios":["S"],
                          "rows":[{"meaning":"reported_CO2_not_a_gross_or_CDR_decomposition"}]}}


def bundle(document=None):
    content = json.dumps(data() if document is None else document).encode()
    manifest = {"schema_version":"1.0.0", "release_id":"pilot", "source_commit":"abc",
                "provenance_type":"PUBLISHED_PUBLIC_TUTORIAL", "metric_id":"reported_co2",
                "identifiability_level":"I0", "publication_permission":"DERIVED_ANALYSIS_ONLY",
                "scientific_status":"COVERAGE_AND_COMPARISON_ONLY",
                "dataset_sha256": hashlib.sha256(content).hexdigest()}
    return manifest, content


def test_coverage_only_briefing_is_explicit_about_limits():
    manifest, raw = bundle()
    text = make_briefing(manifest, raw, milestones=MILESTONES)
    assert "neither residual" not in text.lower() or "Neither residual gross CO2" in text
    assert "reported" in text
    assert "RP-03" in text
    assert "no claims of real external team approvals" in text


def test_hash_mismatch_rejected():
    manifest, raw = bundle()
    with pytest.raises(BriefingError, match="HASH_MISMATCH"):
        make_briefing(manifest, raw+b"x", milestones=MILESTONES)


def test_self_declared_i3_rejected():
    manifest, raw = bundle()
    manifest["identifiability_level"]="I3"
    with pytest.raises(BriefingError):
        make_briefing(manifest, raw, milestones=MILESTONES)


def test_misleading_accounting_flag_rejected():
    d = data()
    d["accounting"]["i3_scenarios"]=10
    manifest, raw = bundle(d)
    with pytest.raises(BriefingError, match="coverage-only"):
        make_briefing(manifest, raw, milestones=MILESTONES)


def test_wrong_source_commit_rejected():
    d = data()
    d["source"]["git_revision"]="other"
    manifest, raw = bundle(d)
    with pytest.raises(BriefingError, match="revision"):
        make_briefing(manifest, raw, milestones=MILESTONES)


def test_signed_decadal_briefing_requires_manifest_bound_sha():
    manifest, raw = bundle()
    t = {"trajectory_schema": "reported_co2_decadal.v1", "variable":"Emissions|CO2",
         "unit":"Mt CO2/yr", "observations":[{"year":2100,"value":-1,"meaning":"reported_CO2_not_a_gross_or_CDR_decomposition"}],
         "year_summaries":[{"year":2100,"matched_observations":1,"negative_reported_co2_count":1}]}
    trajectory = json.dumps(t).encode()
    manifest["decadal_schema"] = "reported_co2_decadal.v1"
    manifest["decadal_sha256"] = hashlib.sha256(trajectory).hexdigest()
    report = make_briefing(manifest, raw, milestones=MILESTONES, trajectory_raw=trajectory)
    assert "1 of 1 matched source observations are negative" in report
    with pytest.raises(BriefingError, match="SHA-256"):
        make_briefing(manifest, raw, milestones=MILESTONES, trajectory_raw=trajectory + b" ")
