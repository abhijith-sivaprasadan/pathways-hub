# PathwaysHub independent user handover (prototype)

**10-minute setup:** Clone repository, install Python >=3.10, execute pip install -e '.[dev]', then python -m pytest -q. Run the existing synthetic intake with: python -m pathways_hub intake --submissions fixtures/team_a.json fixtures/team_b.json fixtures/team_c.json --output outputs/exercise. Confirm 1 accepted schema-only and 2 rejected. Review outputs/exercise/issues.csv and briefing.md. Then run python -m pathways_hub simulate-cycle --output outputs/synthetic_cycle to exercise separately authored fictional corrected submissions and verify the deterministic fixture release digest.

**One-hour external usability session (not yet conducted):** Allocate 10 minutes for onboarding, 15 for initial intake and explanation of issue codes, 15 for correction and repeat validation, 10 for reviewing source SHA and blocked I3 claims, 10 for recording feedback. The tester should not be the author. They must not be represented as an IIASA model developer or reviewer without authorization.

**Evidence collection:** Ask participant for consent in a separate private permissioned record. Record only chosen public aliases/roles if consented, program version, date, actual exercises completed, problems and issue IDs, whether behavior was independently reproduced, and the author's response. Do not store private identities or emails in the public repository. A second distinct non-author user must perform a separate submitter/reviewer action for any external-coordination evidence tier.

**Status:** NO EXTERNAL USER SESSION COMPLETED. SIMULATION_ONLY is the only demonstrated tier. Synthetic fixture acceptance and checksums do not authenticate roles, verify scientific truth or authorize external publication.
