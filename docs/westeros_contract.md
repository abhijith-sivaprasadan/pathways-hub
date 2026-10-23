# Two-repository Westeros evidence contract v1

**Separate from IAMC I0/I3 scientific source releases.** The `consume-westeros` command validates only an allowlisted local MESSAGEix/GAMS Westeros metadata handoff. A successful decision is **ACCEPTED_AUTHOR_REPORTED_LOCAL**, meaning the two files have matching SHA-256 bytes and describe two correctly shaped author-attested tutorial scenarios. This is not independent solver execution, authentication of the author, objective replication, external scientific review, or verification of emissions accounting.

## On the computer where GAMS already ran

Use the exact already-successful ResidualPathways run; no new solve needed:

```powershell
cd 'E:\New folder (2)\MissionJob\residual-pathways'
git pull --ff-only
& .\.venv-messageix\Scripts\python.exe -m residual_pathways westeros-export `
  --input 'results/messageix_private/20261023T230104Z_e182e730/manifest.private.json' `
  --output 'results/westeros_handoff'
```

The output includes only `westeros_evidence.json` and `westeros_evidence.manifest.json`, both under a gitignored folder. **Review these two files before any publication.** Keep all private manifests, raw solver logs, GDX, executable notebooks and GAMS licence information local.

Consume with the standalone PathwaysHub environment:

```powershell
cd 'E:\New folder (2)\MissionJob\pathways-hub'
git pull --ff-only
& .\.venv\Scripts\python.exe -m pathways_hub consume-westeros `
  --manifest '..\residual-pathways\results\westeros_handoff\westeros_evidence.manifest.json' `
  --artifact '..\residual-pathways\results\westeros_handoff\westeros_evidence.json' `
  --output outputs/westeros_contract
Get-Content .\outputs\westeros_contract\decision.json
```

Use `--expected-sha256 <trusted-separately-obtained-digest>` if comparing with an independently held content digest; this protects against someone replacing both files in transit. Reading the digest from the same sidecar file does **not** add independent trust.

## Explicit contract boundary

The sidecar contains exactly: `schema_version`, `artifact_name`, `artifact_sha256`, `artifact_bytes`, `publication_scope`, `attestation`. The artifact contains only a pinned upstream commit, named tutorial/model scope, MESSAGEix/ixmp version, locally declared successful run identifier/status and two stored objectives plus their notebook source hashes and versions.

The verifier fails closed on mismatched size/hash, injected fields, duplicated keys, unexpected origin/scope, incomplete/duplicate scenarios, non-finite objective values and inconsistent version markers. It **does not** fetch the official notebooks to independently confirm their source hashes, verify GAMS licences, or run either optimization.

**Do not call `pathways_hub consume` for the Westeros bundle**: that existing command is an incompatible, independent IAMC coverage/identifiability release contract. The derived `outputs/westeros_contract/decision.json` remains an integrity/semantics decision with explicit `independently_reproduced: false`.

## CI and honest reporting

The [synthetic handoff GitHub Actions workflow](../.github/workflows/westeros-handoff.yml) checks that both repositories interoperate using an **artificial private-manifest fixture**. It deliberately never installs GAMS or performs an actual solve, and its pass state does not validate the 2026-10-24 local GAMS run. A true independent reproduction would require separate executable solver evidence, compatible licence and an independently held input/output hash reference.
