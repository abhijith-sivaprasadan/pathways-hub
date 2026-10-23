"""Multi-step FICTIONAL round with explicit manual fixture corrections, SHA audit.

No real team members, external participants, human approval or scientific
verification exist in this test.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json

from .core import validate_submission, read_json


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def run_simulated_cycle(root, output):
    root=Path(root)
    p=read_json(root/"protocols/v1.json")
    originals={k:read_json(root/f"fixtures/team_{k}.json") for k in "abc"}
    corrected={"b":read_json(root/"fixtures/corrected/team_b.json"),
               "c":read_json(root/"fixtures/corrected/team_c.json")}
    first={k:validate_submission(doc,p,"synthetic_"+k) for k,doc in originals.items()}
    assert [first[k]["status"] for k in "abc"]==[
        "ACCEPTED_SCHEMA_ONLY","REJECTED","REJECTED"],"Synthetic injection assumptions changed"
    decisions=[]
    final={}
    for name in "abc":
        source=originals[name]
        issues=first[name]["errors"]
        if name=="a":
            final[name]=source
            continue
        replacement=corrected[name]
        if (source.get("model"),source.get("scenario"))!=(replacement.get("model"),replacement.get("scenario")):
            raise ValueError("A correction must retain the same synthetic identity")
        if replacement.get("provenance_type")!="SYNTHETIC_TEST_ONLY" or not replacement.get("correction_notice"):
            raise ValueError("Missing fictional correction provenance")
        # No spontaneous imputation or silent unit reinterpretation. Another explicit
        # authored fixture represents a subsequent synthetic submission.
        final[name]=replacement
        decisions.append({
            "issue_id":f"SIM-{name.upper()}-001",
            "evidence_tier":"SIMULATION_ONLY",
            "actor":"FICTIONAL_FIXTURE_AUTHOR",
            "initial_source_sha256":digest(source),
            "corrected_source_sha256":digest(replacement),
            "original_issue_codes":sorted(set(e["code"] for e in issues)),
            "action":"EXPLICIT_AUTHOR_CREATED_CORRECTED_SYNTHETIC_SUBMISSION",
            "correction_notice":replacement["correction_notice"],
            "human_review":False,
        })
    second={k:validate_submission(doc,p,"synthetic_"+k) for k,doc in final.items()}
    if any(x["status"]!="ACCEPTED_SCHEMA_ONLY" for x in second.values()):
        raise RuntimeError("Corrections did not resolve every synthetic protocol error")
    accepted={
        "schema_version":"synthetic-cycle.v1",
        "protocol_version":p["protocol_version"],
        "protocol_sha256":digest(p),
        "evidence_tier":"SIMULATION_ONLY",
        "records":{k:{"source_sha256":digest(final[k]),
                      "status":second[k]["status"],
                      "observations":second[k]["observations"]} for k in "abc"},
    }
    release_hash=digest(accepted)
    report={
        "simulation":"FICTIONAL_THREE_SUBMISSION_ROUND_NO_REAL_PARTICIPANTS",
        "initial_statuses":{k:x["status"] for k,x in first.items()},
        "initial_issue_counts":{k:len(x["errors"]) for k,x in first.items()},
        "corrected_statuses":{k:x["status"] for k,x in second.items()},
        "remaining_issue_count":sum(len(x["errors"]) for x in second.values()),
        "decisions":decisions,
        "accepted_fixture_release_sha256":release_hash,
        "accepted_fixture_manifest":accepted,
        "scientific_approval":"NOT_CLAIMED",
        "human_coordination":"NOT_DEMONSTRATED",
        "warning":"Corrections are separately authored synthetic source fixtures; no real measurements, meetings, partners, or scientific approvals.",
    }
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    (dest/"cycle.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    md=["# Three-team simulated protocol correction exercise","",
        "**SIMULATION ONLY; these are fictional role fixtures, not actual partner teams.**","",
        "Three synthetic initial submissions: one schema-accepted and two rejected.",
        "Two separately authored synthetic corrected-submission files resolve the original issues.",
        f"Accepted fixture release SHA-256: {release_hash}.","",
        "Automated schema acceptance is not scientific endorsement. No real interpersonal coordination or external user testing occurred.",""]
    (dest/"cycle_report.md").write_text("\n".join(md))
    return report
