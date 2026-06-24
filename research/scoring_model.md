# TraceGrid Scoring Model

Generated: 2026-06-24T21:30:46Z

## Impact scale

| Score | Meaning |
| --- | --- |
| 0 | No meaningful degradation |
| 1 | Minor degradation |
| 2 | Moderate degradation |
| 3 | Severe degradation |
| 4 | Catastrophic failure |

## Failure type mapping

| Workflow step | Failure type |
| --- | --- |
| Observe Digital Environment | Input failure |
| Collect Signals | Input failure |
| Filter Noise | Validation failure |
| Corroborate | Validation failure |
| Map Relationships | Interpretation failure |
| Assess Confidence | Confidence failure |
| Produce Understanding | Communication failure |

## Metrics produced

For every profession and for the global corpus:

- Average impact score per step
- Median impact score per step
- Failure frequency per step
- Catastrophic failure frequency per step
- Normalized step importance

## Normalization formula

`importance_raw = average_impact * 0.55 + median_impact * 0.25 + failure_frequency * 1.25 + catastrophic_frequency * 1.75`

`weight = importance_raw / sum(all_step_importance_raw) * 100`

## Why this formula

Average impact captures ordinary degradation. Median impact resists one-off outliers. Failure frequency captures how often a step becomes a practical weakness. Catastrophic frequency ensures that rare but integrity-destroying failures are not washed out by many minor cases.
