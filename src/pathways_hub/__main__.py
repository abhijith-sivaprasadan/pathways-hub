"""Run synthetic IAMC intake and verify published scientific release files."""
import argparse
import json
from pathlib import Path
from .core import read_json, validate_submission, validate_release, write_report


def main():
    parser = argparse.ArgumentParser(description="PathwaysHub research submission QA")
    sub = parser.add_subparsers(dest="command", required=True)
    intake = sub.add_parser("intake")
    intake.add_argument("--protocol", default="protocols/v1.json")
    intake.add_argument("--submissions", nargs="+", required=True)
    intake.add_argument("--output", default="outputs/exercise")
    consume = sub.add_parser("consume")
    consume.add_argument("--manifest", required=True)
    consume.add_argument("--artifact", help="results.json that corresponds to manifest dataset_sha256")
    consume.add_argument("--output", default="outputs/contract")
    review = sub.add_parser("review-ledger", help="Validate checksum event ledger and approval separation")
    review.add_argument("--input", required=True)
    review.add_argument("--output", default="outputs/review/validation.json")
    brief = sub.add_parser("briefing", help="Evidence-locked briefing from exact science artifact")
    brief.add_argument("--manifest", required=True)
    brief.add_argument("--artifact", required=True)
    brief.add_argument("--trajectory", help="Hash-verified supplementary decadal JSON")
    brief.add_argument("--milestones", default="protocols/workstream_v3.json")
    brief.add_argument("--output", default="outputs/briefings/coverage.md")
    cycle = sub.add_parser("simulate-cycle",help="Run FICTIONAL three-team correction and SHA release")
    cycle.add_argument("--root",default=".")
    cycle.add_argument("--output",default="outputs/synthetic_cycle")
    board = sub.add_parser("status-board",help="Generate status tracker from author-declared v3 milestones")
    board.add_argument("--source",default="protocols/workstream_v3.json")
    board.add_argument("--output",default="outputs/v3_status")
    args = parser.parse_args()
    if args.command == "intake":
        p = read_json(args.protocol)
        rows = [validate_submission(read_json(f), p, Path(f).name) for f in args.submissions]
        x = write_report(rows, p, args.output)
        print(f"Simulated intake: {len(rows)} submissions, {x['issue_count']} issues")
    elif args.command == "status-board":
        from .status_board import write_board
        r=write_board(args.source,args.output)
        print("Status board items:",len(r["items"]),"author-declared only")
    elif args.command == "simulate-cycle":
        from .simulation import run_simulated_cycle
        r=run_simulated_cycle(args.root,args.output)
        print("FICTIONAL protocol-correction round accepted:",r["accepted_fixture_release_sha256"])
    elif args.command == "briefing":
        from .briefing import run_briefing
        result = run_briefing(args.manifest, args.artifact, args.milestones, args.output, trajectory_path=args.trajectory)
        print("Wrote evidence-locked briefing:", result)
    elif args.command == "review-ledger":
        from .review import run_review
        result = run_review(args.input, args.output)
        print(result["status"], result["last_state"])
    elif args.command == "consume":
        data = Path(args.artifact).read_bytes() if args.artifact else None
        decision = validate_release(read_json(args.manifest), data)
        target = Path(args.output)
        target.mkdir(parents=True, exist_ok=True)
        (target / "decision.json").write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n")
        print(decision["status"])
        if decision["status"] == "BLOCKED":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
