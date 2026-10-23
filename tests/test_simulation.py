import json
from pathlib import Path
from pathways_hub.simulation import run_simulated_cycle
from pathways_hub.core import read_json, validate_submission

ROOT=Path(__file__).resolve().parents[1]

def test_full_synthetic_round_is_reproducible(tmp_path):
    a=run_simulated_cycle(ROOT,tmp_path/"run1")
    b=run_simulated_cycle(ROOT,tmp_path/"run2")
    assert a==b
    assert a["initial_statuses"]=={"a":"ACCEPTED_SCHEMA_ONLY","b":"REJECTED","c":"REJECTED"}
    assert set(a["corrected_statuses"].values())=={"ACCEPTED_SCHEMA_ONLY"}
    assert a["remaining_issue_count"]==0
    assert len(a["decisions"])==2
    assert a["human_coordination"]=="NOT_DEMONSTRATED"
    assert a["scientific_approval"]=="NOT_CLAIMED"
    assert "SIMULATION ONLY" in (tmp_path/"run1"/"cycle_report.md").read_text()

def test_revised_fixture_needs_current_protocol():
    p=read_json(ROOT/"protocols/v1.json")
    doc=read_json(ROOT/"fixtures/corrected/team_b.json")
    p["protocol_version"]="2.0.0"
    result=validate_submission(doc,p)
    assert result["status"]=="REJECTED"
    assert "PROTOCOL_VERSION_MISMATCH" in {x["code"] for x in result["errors"]}

def test_changed_corrected_values_change_release_hash(tmp_path):
    from pathways_hub.simulation import digest
    d=read_json(ROOT/"fixtures/corrected/team_c.json")
    before=digest(d)
    d["records"][1]["value"]=80
    assert digest(d)!=before
