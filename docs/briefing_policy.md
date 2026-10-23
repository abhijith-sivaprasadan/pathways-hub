# V3 evidence-locked briefings

A workstream briefing is rendered only after the core scientific manifest's source-results bytes pass SHA-256 verification. The current template accepts exactly source schema residualpathways.analysis.v1 and I0 coverage-level claims. It checks source revision agreement, matched row counts, interpretation strings, and the workstream milestone schema. A claim of I3 gross or CDR identifiability is **blocked**, even if someone edits an input manifest to claim that level.

The report contains explicit research-status gates: official source data permissions, reviewed I3 semantics, solver results, and independent participation. It never asserts that the author coordinated real scientists through synthetic fixture tests, that source-reported CO2 is gross residual emissions, or that different model families were controlled causal experiments.

The milestone JSON contains author-reported implementation status; automated briefing software does not independently attest the underlying completed work. GitHub Actions is evidence of the specific tests it executed. No human scientific review process is inferred from the checksum-linked review-log tests.

Run: python -m pathways_hub briefing --manifest PATH/TO/manifest.json --artifact PATH/TO/results.json --milestones protocols/workstream_v3.json --output outputs/briefings/coverage.md
