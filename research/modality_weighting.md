# Phase II Study D: Information Modality Dependency Analysis

Generated: 2026-06-24T22:08:37Z

## Status of this analysis

Mixed observed/inferred architecture model. Phase I professions map imperfectly to TraceGrid collection media, so modality weights blend observed profession weights, global recoverability, and declared medium-specific dependency priors.

## Modality-specific weighting tables

### Web Search Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 10.94 |
| Collect Signals | 19.69 |
| Filter Noise | 11.15 |
| Corroborate | 19.26 |
| Map Relationships | 12.97 |
| Assess Confidence | 19.17 |
| Produce Understanding | 6.82 |

### News Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 10.93 |
| Collect Signals | 20.51 |
| Filter Noise | 10.33 |
| Corroborate | 20.8 |
| Map Relationships | 12.2 |
| Assess Confidence | 19.24 |
| Produce Understanding | 5.99 |

### Social Media Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 8.39 |
| Collect Signals | 16.09 |
| Filter Noise | 18.7 |
| Corroborate | 19.5 |
| Map Relationships | 13.78 |
| Assess Confidence | 18.09 |
| Produce Understanding | 5.45 |

### Public Records Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 17.28 |
| Collect Signals | 17.09 |
| Filter Noise | 7.28 |
| Corroborate | 15.09 |
| Map Relationships | 18.12 |
| Assess Confidence | 14.31 |
| Produce Understanding | 10.83 |

### Academic / Research Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 12.33 |
| Collect Signals | 17.09 |
| Filter Noise | 8.6 |
| Corroborate | 19.77 |
| Map Relationships | 14.79 |
| Assess Confidence | 18.72 |
| Produce Understanding | 8.7 |

### Video / Media Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 11.22 |
| Collect Signals | 18.12 |
| Filter Noise | 11.99 |
| Corroborate | 20.5 |
| Map Relationships | 15.76 |
| Assess Confidence | 16.21 |
| Produce Understanding | 6.2 |

### Forum Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 9.26 |
| Collect Signals | 17.19 |
| Filter Noise | 19.74 |
| Corroborate | 17.99 |
| Map Relationships | 14.15 |
| Assess Confidence | 16.44 |
| Produce Understanding | 5.23 |

### Geospatial / Imagery Agent

| Workflow step | Weight % |
| --- | --- |
| Observe Digital Environment | 16.3 |
| Collect Signals | 18.97 |
| Filter Noise | 8.99 |
| Corroborate | 16.2 |
| Map Relationships | 17.52 |
| Assess Confidence | 16.26 |
| Produce Understanding | 5.76 |

## Cross-modality variation

| Workflow step | Std dev across modalities | Interpretation |
| --- | --- | --- |
| Observe Digital Environment | 2.95 | Moderately variable |
| Collect Signals | 1.41 | Relatively universal |
| Filter Noise | 4.35 | Highly medium-sensitive |
| Corroborate | 1.92 | Moderately variable |
| Map Relationships | 1.96 | Moderately variable |
| Assess Confidence | 1.65 | Moderately variable |
| Produce Understanding | 1.81 | Moderately variable |

## Design implication

TraceGrid should not use one collection-agent weighting profile. Social, forum, video, and web-search agents need heavier noise/corroboration controls; public-records and geospatial agents need stronger observation, relationship mapping, provenance, and confidence preservation.
