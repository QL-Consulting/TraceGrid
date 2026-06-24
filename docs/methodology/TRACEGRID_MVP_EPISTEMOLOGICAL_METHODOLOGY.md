# TraceGrid MVP Epistemological Methodology v0.1

TraceGrid exists to transform uncertainty into defensible confidence through a structured, repeatable, and auditable collection workflow.

TraceGrid does **not** determine truth. TraceGrid produces weighted evidence products that preserve collection method, evidentiary support, uncertainty, limitations, and gaps. Axiom Forge receives those weighted evidence products and performs fusion, validation, contextualization, gap analysis, confidence reassessment, and validated understanding. StratSight governs the decision-support mission context and determines whether confidence is sufficient for operational decision support.

## Canonical Collection-Agent Workflow

Every TraceGrid Collection Agent uses the same methodology regardless of source environment:

1. Observe Environment
2. Collect Signals
3. Filter Noise
4. Corroborate
5. Map Relationships
6. Assess Confidence
7. Produce Understanding

The methodology remains constant. Only the information environment changes.

## Global MVP Weighting Model

| Methodology Step | Step ID | Weight |
|---|---:|---:|
| Observe Environment | `observe_environment` | 13.32% |
| Collect Signals | `collect_signals` | 19.39% |
| Filter Noise | `filter_noise` | 10.77% |
| Corroborate | `corroborate` | 17.37% |
| Map Relationships | `map_relationships` | 14.65% |
| Assess Confidence | `assess_confidence` | 17.89% |
| Produce Understanding | `produce_understanding` | 6.61% |
| **Total** |  | **100.00%** |

## Score Scale

Each workflow step uses the same score scale:

| Score | Meaning |
|---:|---|
| 0 | Not Performed |
| 1 | Poor |
| 2 | Limited |
| 3 | Adequate |
| 4 | Strong |
| 5 | Exceptional |

## Weighted Contribution

For each step:

```text
Step Weighted Contribution = Step Score × Step Weight
```

## Normalized Confidence Score

```text
weighted_score = Σ(step_score × step_weight)
max_weighted_score = 5 × 100
normalized_confidence = weighted_score ÷ max_weighted_score
```

The normalized confidence score is always represented as a value from `0.00` to `1.00`.

## Confidence Bands

| Normalized Confidence | Band |
|---:|---|
| 0.00 – 0.20 | Very Low Confidence |
| 0.21 – 0.40 | Low Confidence |
| 0.41 – 0.60 | Moderate Confidence |
| 0.61 – 0.80 | High Confidence |
| 0.81 – 1.00 | Very High Confidence |

## Required Collection-Agent Output Structure

Every TraceGrid collection-agent assessment artifact must be shaped around the following fields:

- `claim_assessed`
- `sources_examined`
- `signals_collected`
- `noise_removed`
- `corroborating_evidence`
- `contradictory_evidence`
- `relationships_identified`
- `confidence_score`
- `confidence_rationale`
- `collection_gaps`
- `recommended_follow_on_collection`
- `assessment_summary`

Rule: no collection-agent output may represent a conclusion without a confidence rationale. In TraceGrid, `assessment_summary` is a collection assessment summary, not final analytic truth.

## Ecosystem Boundary

```text
Reality
  ↓
TraceGrid
Evidence collection / weighted evidence products
  ↓
Axiom Forge
Analytical reasoning / validation / contextualization / fusion
  ↓
StratSight
Information environment governance / decision support
  ↓
Human Decision Authority
```

TraceGrid owns evidence acquisition, source discovery, collection workflow execution, source-oriented packaging, methodology scoring primitives, and weighted evidence products.

Axiom Forge owns reasoning, interpretation, fusion, validation, contextualization, gap analysis, confidence reassessment, and validated understanding.

StratSight owns governance, confidence sufficiency, decision-support framing, operational relevance, and human-facing decision context.

## Non-Goals for This Phase

This methodology is doctrine and schema-ready architecture. This phase does not implement:

- live scraping providers;
- Firecrawl, ScraperAPI, OpenStreetMap, H3, PostGIS, Mapbox, or other external SDK integrations;
- API keys or environment variables;
- production provider classes;
- production scoring execution;
- database table renames;
- replacement of legacy Paperclip compatibility routes.
