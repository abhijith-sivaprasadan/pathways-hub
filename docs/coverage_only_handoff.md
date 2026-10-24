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

Tests use synthetic aggregates and attack cases (missing entries, altered hashes, false I3 and private record fields). They do not certify an empirical AR6 exchange: the actual four-year source artifact has yet to be generated, reviewed and version-tagged.
