# PathwaysHub

**Live companion science atlas:** [Residual Pathways Atlas](https://residual-pathways-atlas.vercel.app/) — public evidence-first dashboard sourced from versioned ResidualPathways aggregate data. Its displayed workstream statuses are an author-declared snapshot, **not** human-verified scientific approvals or real partner submissions. [Source and scope](https://github.com/abhijith-sivaprasadan/residual-pathways/tree/main/atlas).

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

## Evidence-constrained technical briefing

The briefing command generates a workstream status memo only from a source-artifact-hash-verified ResidualPathways release and an explicitly declared v3 milestone register. It refuses I3/gross claims while data remain I0. See docs/briefing_policy.md. GitHub Actions publishes the reproducible briefing artifact with each upstream-integration run.

The briefing can now verify a supplementary decadal trajectory by its manifest SHA-256 and accurately disclose signed negative CO2 observations without inferring gross emissions.

## Local MESSAGEix/GAMS milestone (2026-10-24)

The author provided terminal output documenting two **actual locally solved** official Westeros training scenarios (baseline and emissions bound) with MESSAGEix 3.11.1, GAMS 54.6.0 and CPLEX. The ResidualPathways runner reported `ACTUAL_MESSAGEIX_GAMS_SOLVED`; [the scoped evidence note](docs/messageix_local_run.md) records objectives and limitations without publishing private solver/licence logs. This is **author-reported local execution**, not independently reproduced CI work or an AR6 source release. RP-07 is marked `DONE_TESTED` for this technical gate; the next gate is sanitized hash-linked publication and independent reproduction.

## Hash-linked Westeros execution handoff

The two-repository v1 pipeline is now implemented: `residual_pathways westeros-export` extracts an allowlisted, local-only two-scenario result from a successful private GAMS manifest, while `pathways_hub consume-westeros` checks exact artifact bytes, SHA-256, expected scenario identities, finite objectives, pinned upstream metadata and evidence scope. This is **not** the existing IAMC I0 scientific contract and does not promote a local terminal transcript to independent solver evidence.

See [the Windows handoff commands and contract limits](docs/westeros_contract.md). [Synthetic integration CI](.github/workflows/westeros-handoff.yml) exercises both packages **without** executing GAMS. No user's private solver files are automatically collected, transmitted, or published.

**Local handoff milestone (2026-10-24):** the author supplied a successful `consume-westeros` terminal transcript: `ACCEPTED_AUTHOR_REPORTED_LOCAL`, `BYTE_HASH_MATCH_AND_SCHEMA_CHECKED` for both persisted ixmp objectives (159025.828125 and 191510.796875). The reported artifact SHA-256 and precision distinction are in [the evidence record](docs/messageix_local_run.md). This is not a public artifact upload, GAMS solve in CI, or independent execution attestation.

## Four-year coverage-only candidate handoff

A separate CLI in [coverage_contract.py](src/pathways_hub/coverage_contract.py) validates the optional ResidualPathways Atlas four-year reporting artifact against an out-of-band SHA-256, its sidecar, full category/year/variable dimensions and explicit REVIEW_PENDING / no-I3 scope. It returns ACCEPTED_COVERAGE_ONLY_UNREVIEWED on successful structural intake and does **not** infer I0 from pending scientific review. The author reported a successful **actual local** empirical handoff on 24 October 2026 against an out-of-band transcript-pinned SHA-256 (and rejection of a deliberately incorrect pin). The author subsequently **approved and published** the exact aggregate-only candidate on 24 October 2026, tagged at [`ar6-coverage-only-v0.1.0-candidate`](https://github.com/abhijith-sivaprasadan/residual-pathways/tree/ar6-coverage-only-v0.1.0-candidate), commit `e64156b7429441836d1fa3b1879d40d9aa814bb0`, with unchanged SHA-256 `489a07276556fdb63774297fbb79fe78ed04ffec831ce05a22d4a338629168ba`. The production Vercel artifact was downloaded and verified by the author; this **does not** establish independent scientific review, publisher authentication, physical gross/CDR accounting, or official IIASA/IPCC endorsement. See [the scoped handoff](docs/coverage_only_handoff.md).
