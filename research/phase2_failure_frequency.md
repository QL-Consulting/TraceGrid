# Phase II Study B: Failure Frequency Analysis

Generated: 2026-06-24T22:08:37Z

## Definitions

- **Failure occurrence frequency:** share of rows where the step impact score is greater than 0.
- **Major failure frequency:** share of rows where the step impact score is 3 or 4.
- **Catastrophic failure frequency:** share of rows where the step impact score is 4.

## Global frequency metrics

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency | Failure count | Major count | Catastrophic count |
| --- | --- | --- | --- | --- | --- | --- |
| Observe Digital Environment | 0.4225 | 0.108 | 0.0047 | 2535 | 648 | 28 |
| Collect Signals | 0.5875 | 0.1698 | 0.0047 | 3525 | 1019 | 28 |
| Filter Noise | 0.3 | 0.0165 | 0.0017 | 1800 | 99 | 10 |
| Corroborate | 0.5522 | 0.1698 | 0.0 | 3313 | 1019 | 0 |
| Map Relationships | 0.5133 | 0.1775 | 0.0 | 3080 | 1065 | 0 |
| Assess Confidence | 0.6432 | 0.1808 | 0.0047 | 3859 | 1085 | 28 |
| Produce Understanding | 0.3985 | 0.0 | 0.0 | 2391 | 0 | 0 |

## Profession-specific frequency tables

### OSINT Intelligence Analyst

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 0.016 | 0.0 | 0.0 |
| Collect Signals | 0.999 | 0.991 | 0.0 |
| Filter Noise | 0.296 | 0.0 | 0.0 |
| Corroborate | 0.999 | 0.991 | 0.0 |
| Map Relationships | 0.293 | 0.0 | 0.0 |
| Assess Confidence | 0.991 | 0.991 | 0.0 |
| Produce Understanding | 0.0 | 0.0 | 0.0 |

### OSINT Investigative Journalist

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 0.187 | 0.0 | 0.0 |
| Collect Signals | 0.187 | 0.0 | 0.0 |
| Filter Noise | 0.051 | 0.035 | 0.0 |
| Corroborate | 0.215 | 0.0 | 0.0 |
| Map Relationships | 0.274 | 0.0 | 0.0 |
| Assess Confidence | 0.215 | 0.0 | 0.0 |
| Produce Understanding | 0.187 | 0.0 | 0.0 |

### Cyber Threat Intelligence Analyst

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 1.0 | 0.0 | 0.0 |
| Collect Signals | 1.0 | 0.0 | 0.0 |
| Filter Noise | 1.0 | 0.0 | 0.0 |
| Corroborate | 1.0 | 0.0 | 0.0 |
| Map Relationships | 1.0 | 1.0 | 0.0 |
| Assess Confidence | 1.0 | 0.0 | 0.0 |
| Produce Understanding | 1.0 | 0.0 | 0.0 |

### Meteorologist / Weather Forecaster

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 0.332 | 0.028 | 0.028 |
| Collect Signals | 0.339 | 0.028 | 0.028 |
| Filter Noise | 0.194 | 0.0 | 0.0 |
| Corroborate | 0.053 | 0.028 | 0.0 |
| Map Relationships | 0.194 | 0.0 | 0.0 |
| Assess Confidence | 0.334 | 0.028 | 0.028 |
| Produce Understanding | 0.14 | 0.0 | 0.0 |

### Quantitative Trader / Market Analyst

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 0.0 | 0.0 | 0.0 |
| Collect Signals | 0.0 | 0.0 | 0.0 |
| Filter Noise | 0.136 | 0.064 | 0.01 |
| Corroborate | 0.169 | 0.0 | 0.0 |
| Map Relationships | 0.319 | 0.0 | 0.0 |
| Assess Confidence | 0.319 | 0.066 | 0.0 |
| Produce Understanding | 0.064 | 0.0 | 0.0 |

### Competitive Intelligence Analyst

| Workflow step | Occurrence frequency | Major frequency | Catastrophic frequency |
| --- | --- | --- | --- |
| Observe Digital Environment | 1.0 | 0.62 | 0.0 |
| Collect Signals | 1.0 | 0.0 | 0.0 |
| Filter Noise | 0.123 | 0.0 | 0.0 |
| Corroborate | 0.877 | 0.0 | 0.0 |
| Map Relationships | 1.0 | 0.065 | 0.0 |
| Assess Confidence | 1.0 | 0.0 | 0.0 |
| Produce Understanding | 1.0 | 0.0 | 0.0 |

## Observed pattern

The corpus separates frequent weakness from catastrophic weakness. Confidence assessment and signal collection fail often; catastrophic failures are rarer and should be interpreted as high-consequence tails rather than everyday events.

## Limitation

Because Phase I final-output quality is derived from step scores, failure frequency is not a causal estimate. It is a workload/architecture pressure estimate: where TraceGrid should expect recurring control burden.
