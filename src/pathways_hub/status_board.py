"""Deterministic status board from declared milestone records, not real meetings."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

SEVERITY={
    "DONE_TESTED":"CLOSED_TESTED_SOFTWARE",
    "IN_PROGRESS":"ACTIVE",
    "NOT_STARTED":"OPEN",
    "BLOCKED":"BLOCKED_EXTERNAL_OR_METHOD",
    "NEEDS_EXTERNAL_REVIEW":"BLOCKED_HUMAN_EVIDENCE",
}

def render_status(plan):
    if plan.get("schema_version")!="workstream.v1":
        raise ValueError("Unknown workstream schema")
    rows=plan.get("milestones")
    if not isinstance(rows,list) or not rows:
        raise ValueError("Missing milestones")
    if len({r.get("id") for r in rows})!=len(rows):
        raise ValueError("Duplicate milestones")
    counts=Counter()
    by_severity=[]
    for row in rows:
        if row.get("status") not in SEVERITY:
            raise ValueError("Unexpected state")
        if any(not isinstance(row.get(k),str) or not row[k] for k in ("id","name","gate")):
            raise ValueError("Missing milestone description/gate")
        item={"id":row["id"],"name":row["name"],"status":row["status"],
              "display_state":SEVERITY[row["status"]],"gate":row["gate"],
              "evidence_url":row.get("evidence_url")}
        counts[row["status"]]+=1
        by_severity.append(item)
    return {"schema":"workstream-status.v1","evidence":"AUTHOR_DECLARED_MILESTONE_STATUS",
            "source_schema":"workstream.v1","counts":dict(counts),
            "items":sorted(by_severity,key=lambda x:x["id"]),
            "warning":"Status reflects author-maintained records, not independently authenticated participant signoff."}

def write_board(source, output):
    d=render_status(json.loads(Path(source).read_text()))
    base=Path(output)
    base.mkdir(parents=True,exist_ok=True)
    (base/"status_board.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    txt=["# v3 research workstream — evidence-scoped status","","**Author-declared statuses; no official IIASA affiliation or external coordination claim.**","",
         "| Milestone | Status | Acceptance gate |","|---|---|---|"]
    for row in d["items"]:
        txt.append(f"| {row['id']} — {row['name']} | {row['display_state']} | {row['gate']} |")
    txt+=["","Counts by author-declared source states: "+", ".join(f"{k}={v}" for k,v in sorted(d["counts"].items()))+".",
           "Model-specific scientific review, source access, solver licensing and external participation are distinct gates; software test success does not satisfy them.",""]
    (base/"status_board.md").write_text("\n".join(txt))
    return d
