# Phase II Study C: Recoverability Analysis

Generated: 2026-06-24T22:08:37Z

## Status of this analysis

**Inferred architectural model, not directly observed counterfactual evidence.** The Phase I corpus records failed/weak steps and degraded outputs, but it does not run alternate histories where downstream stages repair upstream failures. This study therefore blends:

1. a declared workflow-structure prior, and
2. observed Phase I failure propagation, major-failure rate, catastrophic-failure rate, downstream burden, and downstream-clean rate.

## Recovery scale

| Score band | Meaning |
| --- | --- |
| 0 | Fully Recoverable |
| 1 | Mostly Recoverable |
| 2 | Partially Recoverable |
| 3 | Rarely Recoverable |
| 4 | Not Recoverable |

## Global recoverability model

| Workflow step | Recoverability score | Recovery label | Structural prior | Observed non-recovery | Major given failure | Downstream clean rate |
| --- | --- | --- | --- | --- | --- | --- |
| Observe Digital Environment | 2.187 | Partially Recoverable | 2.4 | 1.84 | 0.2556 | 0.0004 |
| Collect Signals | 3.229 | Rarely Recoverable | 4.0 | 1.971 | 0.2891 | 0.0017 |
| Filter Noise | 2.171 | Partially Recoverable | 2.6 | 1.471 | 0.055 | 0.0761 |
| Corroborate | 2.748 | Rarely Recoverable | 3.2 | 2.01 | 0.3076 | 0.0033 |
| Map Relationships | 2.057 | Partially Recoverable | 2.2 | 1.824 | 0.3458 | 0.0756 |
| Assess Confidence | 2.659 | Rarely Recoverable | 3.5 | 1.288 | 0.2812 | 0.3804 |
| Produce Understanding | 0.683 | Mostly Recoverable | 1.0 | 0.167 | 0.0 | 1.0 |

## Profession-specific recoverability scores

### OSINT Intelligence Analyst

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 2.109 | Partially Recoverable | 1.634 |
| Collect Signals | 3.783 | Not Recoverable | 3.43 |
| Filter Noise | 2.238 | Partially Recoverable | 1.648 |
| Corroborate | 3.287 | Rarely Recoverable | 3.428 |
| Map Relationships | 1.981 | Partially Recoverable | 1.624 |
| Assess Confidence | 3.044 | Rarely Recoverable | 2.3 |
| Produce Understanding | 0.62 | Mostly Recoverable | 0.0 |

### OSINT Investigative Journalist

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 1.763 | Partially Recoverable | 0.723 |
| Collect Signals | 2.755 | Rarely Recoverable | 0.723 |
| Filter Noise | 2.511 | Rarely Recoverable | 2.365 |
| Corroborate | 2.295 | Partially Recoverable | 0.817 |
| Map Relationships | 1.434 | Mostly Recoverable | 0.185 |
| Assess Confidence | 2.432 | Partially Recoverable | 0.689 |
| Produce Understanding | 0.639 | Mostly Recoverable | 0.05 |

### Cyber Threat Intelligence Analyst

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 2.115 | Partially Recoverable | 1.65 |
| Collect Signals | 3.107 | Rarely Recoverable | 1.65 |
| Filter Noise | 2.208 | Partially Recoverable | 1.568 |
| Corroborate | 2.611 | Rarely Recoverable | 1.65 |
| Map Relationships | 2.563 | Rarely Recoverable | 3.155 |
| Assess Confidence | 2.576 | Rarely Recoverable | 1.068 |
| Produce Understanding | 0.639 | Mostly Recoverable | 0.05 |

### Meteorologist / Weather Forecaster

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 1.955 | Partially Recoverable | 1.228 |
| Collect Signals | 2.934 | Rarely Recoverable | 1.196 |
| Filter Noise | 1.715 | Partially Recoverable | 0.272 |
| Corroborate | 2.867 | Rarely Recoverable | 2.323 |
| Map Relationships | 1.707 | Partially Recoverable | 0.902 |
| Assess Confidence | 2.453 | Partially Recoverable | 0.744 |
| Produce Understanding | 0.639 | Mostly Recoverable | 0.05 |

### Quantitative Trader / Market Analyst

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 1.488 | Mostly Recoverable | 0.0 |
| Collect Signals | 2.48 | Partially Recoverable | 0.0 |
| Filter Noise | 2.543 | Rarely Recoverable | 2.449 |
| Corroborate | 2.336 | Partially Recoverable | 0.926 |
| Map Relationships | 1.757 | Partially Recoverable | 1.034 |
| Assess Confidence | 2.474 | Partially Recoverable | 0.8 |
| Produce Understanding | 0.639 | Mostly Recoverable | 0.05 |

### Competitive Intelligence Analyst

| Workflow step | Recoverability score | Recovery label | Observed non-recovery |
| --- | --- | --- | --- |
| Observe Digital Environment | 2.418 | Partially Recoverable | 2.446 |
| Collect Signals | 2.985 | Rarely Recoverable | 1.33 |
| Filter Noise | 1.878 | Partially Recoverable | 0.7 |
| Corroborate | 2.473 | Partially Recoverable | 1.287 |
| Map Relationships | 1.908 | Partially Recoverable | 1.431 |
| Assess Confidence | 2.539 | Rarely Recoverable | 0.971 |
| Produce Understanding | 0.745 | Mostly Recoverable | 0.329 |

## Interpretation

- **Collect Signals** is modeled as the least recoverable step. If evidence was never collected, later corroboration and confidence scoring mostly operate on absence, not evidence.
- **Assess Confidence** is rarely recoverable because an overconfident or underconfident handoff contaminates downstream decisions even if the evidence exists.
- **Map Relationships** is partially recoverable when evidence/provenance remains intact; analysts can rebuild graph structure after the fact.
- **Produce Understanding** is the most recoverable step because a bad report or handoff can often be rewritten if evidence, provenance, and confidence state remain intact.

## Human adjudication needed

A stronger Phase III design should sample high-impact rows and ask domain experts whether actual recovery occurred: Was missing collection repaired by later collection? Did confidence calibration prevent misuse? Did relationship mapping errors propagate to decision makers?
