"""Generate decision-usable briefing only from hash-verified scientific output.

No summary of gross emissions is permitted from an I0-I2 or missing-accounting
release; semantic gate and provenance survive downstream transformations.
"""
from __future__ import annotations
from pathlib import Path
import json
from .core import validate_release


class BriefingError(ValueError):
    pass


def make_briefing(manifest: dict, artifact: bytes, *, milestones: dict) -> str:
    decision = validate_release(manifest, artifact)
    if decision["status"] == "BLOCKED":
        raise BriefingError("Science release blocked: " + "; ".join(decision["problems"]))
    try:
        data = json.loads(artifact.decode("utf-8"))
    except (UnicodeError, ValueError) as e:
        raise BriefingError("Scientific artifact must be UTF-8 JSON") from e
    if not isinstance(data, dict) or data.get("schema_version") != "residualpathways.analysis.v1":
        raise BriefingError("Unexpected upstream schema; never guess field meanings")
    if data.get("source", {}).get("git_revision") != manifest["source_commit"]:
        raise BriefingError("Source revision differs between manifest and artifact")
    if data.get("accounting", {}).get("i3_scenarios") != 0 or manifest.get("identifiability_level") != "I0":
        raise BriefingError("This briefing template accepts coverage-only I0 data, not gross/CDR")
    if not isinstance(milestones, dict) or milestones.get("schema_version") != "workstream.v1":
        raise BriefingError("Unreviewed workstream milestones format")
    comparison = data["comparison"]
    if any(row.get("meaning") != "reported_CO2_not_a_gross_or_CDR_decomposition" for row in comparison["rows"]):
        raise BriefingError("Unexpected scientific interpretation label")
    if comparison["matched_rows"] != len(comparison["rows"]):
        raise BriefingError("Matched-row count does not equal source records")
    status = decision["status"]
    out = [
        "# IAMC evidence and workstream status briefing",
        "",
        "**Automatically generated; evidence-scope checked; NOT an IIASA publication or policy recommendation.**",
        "",
        "## Scientific evidence",
        "",
        f"- Source release: {manifest['release_id']}; exact git revision {manifest['source_commit']}.",
        f"- Scientific handoff: {status}; accounting identifiability {manifest['identifiability_level']}.",
        f"- Dataset input sha256: {manifest.get('input_sha256', 'not declared')}.",
        f"- Reported, non-decomposed 2050 World CO2 observations: {comparison['matched_rows']} "
        f"across {len(comparison['cohort_models'])} model versions "
        f"and {len(comparison['common_scenarios'])} common scenario labels.",
        "- Shared scenario labels do not establish controlled comparisons, harmonized assumptions or causal impacts.",
        "- Neither residual gross CO2 nor carbon dioxide removal was identified from this source.",
        "",
        "## Workstream deliverables (declared implementation status; no invented people or sign-offs)",
        "",
        "| Milestone | Status | Gate |",
        "|---|---|---|",
    ]
    allowed_statuses = {"DONE_TESTED", "NOT_STARTED", "BLOCKED", "IN_PROGRESS", "NEEDS_EXTERNAL_REVIEW"}
    for item in milestones.get("milestones", []):
        if (not isinstance(item, dict) or not all(x in item for x in ("id", "name", "status", "gate"))
                or item["status"] not in allowed_statuses):
            raise BriefingError("Unrecognised milestone or unsupported status")
        for k in ("id", "name", "gate"):
            if not isinstance(item[k], str) or "|" in item[k] or "\n" in item[k]:
                raise BriefingError("Invalid milestone field for Markdown table")
        out.append(f"| {item['id']}: {item['name']} | {item['status']} | {item['gate']} |")
    out += ["", "## Decisions for real work",
            "",
            "1. Acquire licensed AR6 World v1.1 and metadata through the official IIASA explorer; record exact source permissions.",
            "2. Audit variable coverage and accounting semantics before computing gross, net, fossil CCS or CDR.",
            "3. Execute an official MESSAGEix/GAMS baseline with solver logs before asserting framework experience.",
            "4. Invite independent consenting submitter/reviewer participants before asserting cross-team coordination.",
            "",
            "This document intentionally makes no claims of real external team approvals, independent verification or model calibration.",
            ""]
    return "\n".join(out)


def run_briefing(manifest_path, artifact_path, milestones_path, output):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    raw = Path(artifact_path).read_bytes()
    milestones = json.loads(Path(milestones_path).read_text(encoding="utf-8"))
    doc = make_briefing(manifest, raw, milestones=milestones)
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")
    return p
