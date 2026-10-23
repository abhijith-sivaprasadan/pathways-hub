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

Objective difference: **32484.973799 native objective units**, or approximately **20.43%** above baseline. This is a *stylized tutorial comparison*, not a real-world cost estimate, not an AR6 scenario, and not evidence of physically decomposed gross CO2/CDR.

The final local runner output included:

```text
Status: ACTUAL_MESSAGEIX_GAMS_SOLVED
```

The author reported the manifest at `results/messageix_private/20261023T230104Z_e182e730/manifest.private.json` on their own machine. **That private manifest and its original output files have not been provided to this repository or independently hash-verified by PathwaysHub.** The runner's status is supported here by the author-supplied terminal transcript only.

## Remaining verification / publication gates

1. On the author's computer, inspect the saved `manifest.private.json` and confirm both `solved_scenarios` entries have `has_solution: true` and finite objective values.
2. Generate a **new, sanitized public evidence summary** with explicit source commit, runner revision, GAMS/MESSAGEix/solver versions, scenario names/objectives and integrity hashes for publishable derived files. Never publish raw GAMS logs, licence identifiers, access codes, GDX files, the HSQLDB database, or private executed notebooks.
3. Add a dedicated, fail-closed local-execution evidence contract to PathwaysHub before treating any submitted summary as machine-verified. The existing `consume` command validates a **different** IAMC I0 coverage release and must not accept a Westeros manifest as if it were that product.
4. Seek independent reproduction and scientific review separately. These educational optimizations do not close AR6 source access, I3 accounting, or external participant gates.

The console log also emitted notices that variables `I` and `C` were not found in GDX, despite both solver runs reaching normal completion and the runner completing its post-solve validation. Those notices warrant investigation before stronger claims about output completeness.
