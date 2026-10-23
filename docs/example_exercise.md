# Simulated intake exercise — worked example

Three test submissions were built by the tool author and are labelled SYNTHETIC_TEST_ONLY.

- Synthetic-A provides World/Emissions|CO2 records in Mt CO2/yr for both required years. Expected: ACCEPTED_SCHEMA_ONLY.
- Synthetic-B provides the same variable in Gt CO2/yr instead of the required Mt CO2/yr. Expected: REJECTED with UNIT_MISMATCH and missing required correctly unit-labelled observations.
- Synthetic-C provides only the 2030 observation, not 2050. Expected: REJECTED with REQUIRED_OBSERVATION_MISSING.

These failures deliberately preserve invalid values rather than silently converting units or imputing missing years. The CLI emits an issue.csv registry and a generated Markdown briefing. Nothing here is an approved scientific submission; no independent reviewers have participated.

The separate integration workflow consumes an actual source-derived result from ResidualPathways. It must return READY_COVERAGE_ONLY because the source's aggregated CO2 reporting does not identify residual gross emissions.
