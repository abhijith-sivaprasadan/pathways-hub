# Locally executed MESSAGEix/GAMS Westeros — scope-limited evidence

**Evidence state: AUTHOR-REPORTED_LOCAL_EXECUTION.** This note summarizes a Windows execution transcript supplied by the project author on 2026-10-24. It is **not** an independent execution by GitHub CI, a signed third-party audit, or an IIASA/AR6 scientific source release.

## What was actually run

- Engine: **MESSAGEix 3.11.1 / ixmp 3.11.1**, using **GAMS 54.6.0** and **CPLEX** (the solver identified itself as running under a demo licence).
- Source: official pinned Westeros baseline and emissions-bound tutorial notebooks at [upstream MESSAGEix commit `2d521407a430a08de997a771e7b38d88f7e7d2b6`](https://github.com/iiasa/message_ix/tree/2d521407a430a08de997a771e7b38d88f7e7d2b6/tutorial/westeros).
- Local runner: [ResidualPathways `messageix_westeros.py`](https://github.com/abhijith-sivaprasadan/residual-pathways/blob/main/src/residual_pathways/messageix_westeros.py), with the scalar objective handling fix at [commit `27984f8`](https://github.com/abhijith-sivaprasadan/residual-pathways/commit/27984f8fce19fbae8532cdd12a70a953395e5bc0).
- The run used a private ixmp HSQLDB database; both scenarios completed GAMS execution with **LP status optimal** and **normal completion**, and the runner subsequently read solved objectives from ixmp.

| Scenario | LP objective (native units) | GAMS/CPLEX status |
| --- | ---: | --- |
| Westeros baseline | 159025.830480 | Optimal |
| Westeros emissions bound | 191510.804279 | Optimal |

These figures are the **GAMS/CPLEX console objectives**, not the rounded scalar values persisted in ixmp. The console-objective difference is **32484.973799 native objective units**, or about **20.43%** above baseline. The separate, hash-linked export below correctly uses the persisted ixmp objectives, not an invented higher-precision database value. This is a *stylized tutorial comparison*, not a real-world cost estimate, not an AR6 scenario, and not evidence of physically decomposed gross CO2/CDR.

The final local runner output included:

```text
Status: ACTUAL_MESSAGEIX_GAMS_SOLVED
```

The original private manifest remains on the author's computer at `results/messageix_private/20261023T230104Z_e182e730/manifest.private.json`. It was not uploaded to this repository.

## Local evidence handoff — completed, author reported (2026-10-24)

The author supplied a second Windows PowerShell transcript confirming:

1. Inspection of that **private ixmp manifest**, which reported `ACTUAL_MESSAGEIX_GAMS_SOLVED` and `has_solution: true` for both scenarios.
2. The new `residual_pathways westeros-export` command successfully produced a **sanitized, derived two-file bundle** in a gitignored output directory.
3. `pathways_hub consume-westeros` read those two files locally and emitted **`ACCEPTED_AUTHOR_REPORTED_LOCAL`** with integrity state **`BYTE_HASH_MATCH_AND_SCHEMA_CHECKED`**.

The reported integrity digest of `westeros_evidence.json` is:

```text
SHA-256: f8da4d0ddacc35758e48b1c1396b89867cc9ed0e7e55ed8a1abba708a3dc3fe1
```

The exported **persisted ixmp** objectives (native units) are **159025.828125** for baseline and **191510.796875** for emissions-bound; difference **32484.968750** and increase **20.427479694974863%**. Small differences from GAMS console objectives are observable and must not be silently erased.

**Verification boundary:** the actual sanitized bundle was validated by the author's *local* PathwaysHub process and is **not stored or independently reproduced here**. The hash shown above is author-reported from local output and has not been independently recomputed from published artifact bytes. An author could replace both local files and recompute a matching checksum; this is byte integrity and schema validation, not cryptographic signer authentication, execution attestation or external scientific review.

## Remaining verification / publication gates

1. Optionally publish the two **manually inspected sanitized derived** JSON files and independently recompute the recorded SHA-256. Never publish raw GAMS console logs, licence identifiers, access codes, GDX files, HSQLDB files, or private executed notebooks.
2. Capture an independent reproducible run with separately obtained input hashes, environment/solver metadata, recorded run/optimality evidence and blinded review. No GitHub CI job has executed the locally licensed GAMS solver.
3. The existing `consume` command is an unrelated IAMC I0 coverage release contract; `consume-westeros` does **not** close AR6 source access, I3 emissions accounting or external-participant scientific-review gates.

The console log also emitted notices that variables `I` and `C` were not found in GDX, despite both solver runs reaching normal completion and the runner completing its post-solve validation. Those notices warrant investigation before stronger claims about output completeness.
