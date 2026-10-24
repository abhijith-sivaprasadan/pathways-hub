# Four-year AR6 coverage-only handoff (candidate)

The new, *separate* public reporting-coverage intake accepts the bytes of ResidualPathways' four-year Atlas coverage JSON **only when an exact out-of-band SHA-256 is supplied**. It checks an accompanying SHA file, the release's fixed schema, C1–C8 × 2030/2050/2070/2100 dimensional completeness, denominator integrity and non-promotable scientific status.

This contract does **not** use the older I0–I3 emission-accounting release path, because *scientific review pending* and *insufficient source information (I0)* have different meanings.

Example Windows PowerShell after the source file has been generated and reviewed in ResidualPathways:

~~~powershell
$source='E:\New folder (2)\MissionJob\residual-pathways\atlas\data\coverage_release.json'
$sidecar="$source.sha256"
$sha=(Get-FileHash $source -Algorithm SHA256).Hash.ToLowerInvariant()
python -m pathways_hub.coverage_contract --artifact $source --sha-file $sidecar --expected-sha256 $sha --output outputs/coverage-contract/status.json
~~~

**For a real frozen release**, obtain the out-of-band expected SHA from the reviewed, immutable upstream release/tag, **not** by calculating it from the untrusted input you are attempting to verify. The example above demonstrates local functionality and is not an independent provenance check.

On success the output status is ACCEPTED_COVERAGE_ONLY_UNREVIEWED, the scientific identifiability status is NOT_ASSESSED, and verified I3 remains zero. The intake does not certify source permissions, scenario-model independence, the official portal receipt, independent research findings, gross residual emissions or atmospheric removals. This is structural-and-byte contract verification only.

Tests use synthetic aggregates and attack cases (missing entries, altered hashes, false I3 and private record fields). These alone do not certify an empirical AR6 exchange.

## Author-reported actual empirical intake on 24 October 2026

The author subsequently supplied terminal evidence of the **real locally generated** 352-record, 1,202-model-scenario ResidualPathways AR6 coverage artifact being accepted by this distinct PathwaysHub module. `ACCEPTED_COVERAGE_ONLY_UNREVIEWED` was returned with 11 variables, `scientifically_reviewed=False`, `identifiability=NOT_ASSESSED`, and `verified_i3=0`; the received SHA-256 was `489a07276556fdb63774297fbb79fe78ed04ffec831ce05a22d4a338629168ba`. A deliberately incorrect expected SHA-256 resulted in `BLOCKED` with nonzero exit. The valid pin came from an earlier author-reported local transcript rather than recomputation within the receiving command.

**Scope:** this verifies real local cross-project byte-integrity/schema handling, not public upload, frozen Git tag, IIASA acquisition authenticity, license clearance, external independent validation, physical carbon flow partition or reviewer sign-off. The public candidate remains **uncommitted** pending [local disclosure/rights review](https://github.com/abhijith-sivaprasadan/residual-pathways/blob/main/docs/ar6_coverage_publication_audit_20261024.md).
