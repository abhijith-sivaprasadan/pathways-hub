# Science → research operations handoff (working integration)

The integration workflow checks out a **specific committed version** of ResidualPathways (not mutable upstream main), runs its source-pinned real IAMC tutorial-data analysis, then provides PathwaysHub both the resulting manifest and *actual results.json bytes*. The source SHA-256 is checked before accepting the release.

This is a real software-integration test on a legitimate published IAMC tutorial dataset. It is not a claim that three external modelling teams participated, nor evidence that a reviewed gross/net/CDR partition has been found.

Expected current result: READY_COVERAGE_ONLY with accounting level I0. An earlier or later A study with insufficient reporting must retain the same downgrade. The hub must not produce or imply gross residual emissions based on tutorial Emissions|CO2 alone.

To update pinned science, first review source changes and run its CI, then change the commit in .github/workflows/upstream-integration.yml in a reviewed commit. The handoff does not edit scientific results.
