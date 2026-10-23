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
    args = parser.parse_args()
    if args.command == "intake":
        p = read_json(args.protocol)
        rows = [validate_submission(read_json(f), p, Path(f).name) for f in args.submissions]
        x = write_report(rows, p, args.output)
        print(f"Simulated intake: {len(rows)} submissions, {x['issue_count']} issues")
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
