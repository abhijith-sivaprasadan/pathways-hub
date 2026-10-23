# Operations protocol

Automated states: intake -> ACCEPTED_SCHEMA_ONLY or REJECTED. Incomplete, duplicate or incompatible submissions are never silently repaired, cast to a new unit, or imputed. Acceptance means structure and protocol compliance only; scientific peer review and publication authorization require actual designated humans.

Evidence tiers:
- SIMULATION_ONLY: automated tests, synthetic submissions and briefings.
- EXTERNALLY_EXERCISED: only after at least two consenting independent non-author participants have undertaken actual submitter/reviewer roles, with permissioned evidence of specific actions. No such exercise is claimed in this release.

Failure records retain submission, severity, code and reason in issues.csv. Decision records and milestones are a planned feature, not fabricated as an achieved human review.

Science releases from ResidualPathways must be immutable inputs with SHA-256 hashes. A source release can be a coverage-only research product; inability to measure gross/net/CDR does not authorize downstream fabrication. Human interpretation and license checks remain separate from automated schema validation.

## I3 safeguard

An I3 manifest label is insufficient on its own. The exact source results JSON must include nonempty verified_i3_records with explicit true semantic-completeness, source-precision, materiality, numerical reconciliation and provenance gates. Even when these checks pass, the hub returns READY_FOR_HUMAN_SCIENTIFIC_REVIEW; it never issues scientific endorsement automatically.
