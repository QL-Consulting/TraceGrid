# TraceGrid Final Phase II Weighting Model

Generated: 2026-06-24T22:08:37Z

## Composite formula

`Final Step Weight = (0.40 x Failure Impact) + (0.30 x Failure Frequency) + (0.30 x Recoverability)`

Failure Impact and Failure Frequency are observed from the Phase I corpus. Recoverability is inferred from workflow structure plus observed failure propagation. The raw composite is normalized to 100%.

## Final global TraceGrid weighting

| Workflow step | Failure impact component | Failure frequency component | Recoverability component | Raw composite | Final weight % |
| --- | --- | --- | --- | --- | --- |
| Observe Digital Environment | 0.8595 | 0.999 | 2.187 | 1.2996 | 13.32 |
| Collect Signals | 1.249 | 1.4155 | 3.229 | 1.893 | 19.39 |
| Filter Noise | 0.5318 | 0.6241 | 2.171 | 1.0513 | 10.77 |
| Corroborate | 1.171 | 1.3421 | 2.748 | 1.6954 | 17.37 |
| Map Relationships | 1.0762 | 1.2751 | 2.057 | 1.4301 | 14.65 |
| Assess Confidence | 1.214 | 1.5423 | 2.659 | 1.746 | 17.89 |
| Produce Understanding | 0.5018 | 0.797 | 0.683 | 0.6447 | 6.61 |

## Recommended architecture priority

1. **Collect Signals** - 19.39%
2. **Assess Confidence** - 17.89%
3. **Corroborate** - 17.37%
4. **Map Relationships** - 14.65%
5. **Observe Digital Environment** - 13.32%
6. **Filter Noise** - 10.77%
7. **Produce Understanding** - 6.61%

## Interpretation

The Phase II model shifts architectural emphasis away from a pure observed-frequency view and toward non-recoverable evidence operations. Collection, confidence assessment, corroboration, and relationship mapping form the core TraceGrid architecture. Produce Understanding remains important for decision handoff, but it should not receive the same infrastructure weight as evidence capture and confidence preservation because it is more recoverable when upstream state is intact.
