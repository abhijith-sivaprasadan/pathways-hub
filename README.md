# PathwaysHub

A research-operations tool to validate incoming IAMC scenario submissions against a versioned protocol and produce an audit trail. **Independent open-source project**, not affiliated with IIASA. This first release tests a synthetic multi-source scenario; it does not claim to have coordinated real modelling teams.

## Reproduce

Requires Python 3.10+.

    python -m pip install -e ".[dev]"
    python -m pytest -q
    python -m pathways_hub intake --protocol protocols/v1.json --submissions fixtures/team_a.json fixtures/team_b.json fixtures/team_c.json --output outputs/exercise

Inspect outputs/exercise/status.json, issues.csv and briefing.md. Three **SYNTHETIC_TEST_ONLY** inputs exercise (1) an accepted schema, (2) a rejected incompatible unit, and (3) a rejected missing scenario year. These are not actual MESSAGEix/REMIND/IMAGE submissions.

## Consume a scientific release

    python -m pathways_hub consume --manifest PATH/TO/release/manifest.json --artifact PATH/TO/results.json --output outputs/contract

The manifest must declare a source version, identity, publication permission and SHA-256 of the exact supplied results.json bytes. Missing/mismatched hashes, incompatible versions, unsupported I3 assertions or missing artifacts fail closed. A correct I0–I2 release stays coverage-only; neither the hub nor its report may upgrade it to gross-emissions evidence.

The science companion is https://github.com/abhijith-sivaprasadan/residual-pathways. These projects use a v1 release contract, not hidden cross-repository edits.

## Uncompleted research-operations work

Actual outside participants and independent expert review; human scientific approval; multi-party decision and milestone register; long-term publication workflow; confidential submission handling. A simulated test is evidence of working software, not evidence of managing an international consortium.

See docs/operations.md and docs/roadmap.md.

## Human review workflow scaffold

The review-ledger command validates a checksum-linked research review chain with distinct schema, review, approval and publication states, including negative tests for forged modifications, self-review and simulated approval. There is **no** real external participant or authentication system in this prototype. See docs/review_protocol_v2.md.
