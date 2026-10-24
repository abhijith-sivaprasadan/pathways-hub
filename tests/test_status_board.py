import json
from pathlib import Path
import pytest
from pathways_hub.status_board import render_status,write_board

ROOT=Path(__file__).resolve().parents[1]

def test_status_board_from_real_declared_milestones(tmp_path):
    d=write_board(ROOT/"protocols/workstream_v3.json",tmp_path)
    assert d["counts"]["NEEDS_EXTERNAL_REVIEW"] == 4
    assert d["counts"]["IN_PROGRESS"] == 4
    assert d["counts"]["DONE_TESTED"] == 17
    assert len(d["items"])>=10
    assert all(x["display_state"] for x in d["items"])
    assert "no official IIASA" in (tmp_path/"status_board.md").read_text()

def test_invalid_duplicate_and_unknown_status():
    d={"schema_version":"workstream.v1","milestones":[{"id":"X","name":"N","gate":"G","status":"DONE_TESTED"}]}
    assert render_status(d)["counts"]=={"DONE_TESTED":1}
    d["milestones"].append(dict(d["milestones"][0]))
    with pytest.raises(ValueError,match="Duplicate"):
        render_status(d)
    d["milestones"].pop()
    d["milestones"][0]["status"]="ENDORSED_BY_IIASA"
    with pytest.raises(ValueError,match="Unexpected"):
        render_status(d)
