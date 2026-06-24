# TraceGrid Global Weighting Scale

Generated: 2026-06-24T21:30:46Z

Corpus size: 6,000 real-world, source-linked case rows (6,000 included in global metrics).

## Result

| Workflow step | Preliminary % | Observed weight % | Avg impact | Median | Failure freq | Catastrophic freq |
| --- | --- | --- | --- | --- | --- | --- |
| Observe Digital Environment | 5 | 11.3 | 0.8595 | 0.0 | 0.4225 | 0.0047 |
| Collect Signals | 20 | 18.81 | 1.249 | 1.0 | 0.5875 | 0.0047 |
| Filter Noise | 15 | 7.51 | 0.5318 | 0.0 | 0.3 | 0.0017 |
| Corroborate | 20 | 17.74 | 1.171 | 1.0 | 0.5522 | 0.0 |
| Map Relationships | 15 | 16.61 | 1.0762 | 1.0 | 0.5133 | 0.0 |
| Assess Confidence | 20 | 19.36 | 1.214 | 1.0 | 0.6432 | 0.0047 |
| Produce Understanding | 5 | 8.67 | 0.5018 | 0.0 | 0.3985 | 0.0 |

## Interpretation

The observed scale moves weight toward the workflow's integrity controls: signal collection, corroboration, relationship mapping, and confidence assessment. Observation and final communication remain necessary gates, but they usually become catastrophic only when they prevent all downstream work or when the final handoff hides uncertainty.

Most important overall in this coded corpus: **Assess Confidence**.

This scale should be treated as an evidence-based first calibration, not a final scientific law. The dataset uses high-volume public catalogs and proxy coding, with row-level confidence fields to support later expert audit.
