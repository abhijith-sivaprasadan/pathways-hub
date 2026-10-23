# Review states and evidence-grade protocol v2

This first implementation supports a checksum-linked event ledger, separate schema acceptance, reviewer evidence, correction/resubmission, withdrawal and publication permission. Every event has an explicit timezone-aware timestamp, event ID, actor role, previous SHA and own SHA.

**Critical boundary:** a SHA chain is *tamper-evident when checked against an independently held original head*, but it is not a digital signature, user authentication or proof that named participants acted. The current synthetic tests use invented test identities and produce SIMULATED_APPROVAL_ONLY, never scientific endorsement or real coordination. A valid chain does not imply that any assertion in an event is true.

Transitions: DRAFT -> SUBMITTED -> ACCEPTED_SCHEMA_ONLY -> IN_REVIEW -> HUMAN_APPROVED_REVIEW, with CHANGES_REQUESTED -> RESUBMITTED and WITHDRAWN terminal state. A second non-submitter reviewer must cite a source artifact for decisions. Actual publication additionally requires PUBLIC_DERIVED permission and a distinct publisher. Live use must add authenticated identities, access controls, consent and human validation before events can constitute verified external research work.

Run: python -m pathways_hub review-ledger --input PATH/TO/ledger.json --output outputs/review/validation.json

Evidence-grade EXTERNALLY_EXERCISED also requires an external_verification_ref; this is a declared requirement, not independent authentication, and cannot by itself certify outside participation.
