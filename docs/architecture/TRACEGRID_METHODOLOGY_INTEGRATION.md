# TraceGrid Methodology Integration Architecture

This document describes how the TraceGrid MVP Epistemological Methodology enters the codebase without enabling new production runtime behavior.

## Purpose

TraceGrid is the Evidence Intelligence Platform in the broader governing intelligence ecosystem. Its mission is to transform uncertainty into defensible confidence through a structured, repeatable, and auditable epistemological workflow.

The platform produces weighted evidence products. It does not determine final truth.

## Additive Architecture Boundary

The methodology integration is intentionally additive:

- shared TypeScript constants define methodology step IDs, labels, weights, score scale, confidence bands, and output-shape types;
- a pure utility calculates normalized confidence from explicit step scores;
- documentation establishes doctrine and ecosystem boundaries;
- no provider runtime, external SDK, database rename, production scoring engine, or collection-agent behavior change is introduced.

## Shared Contract Layer

The shared package exposes methodology primitives that future UI panels, API payload validators, and provider orchestration code can reuse:

- `TRACEGRID_METHODOLOGY_STEP_IDS`
- `TRACEGRID_METHODOLOGY_STEP_LABELS`
- `TRACEGRID_METHODOLOGY_STEP_WEIGHTS`
- `TRACEGRID_METHODOLOGY_SCORE_VALUES`
- `TRACEGRID_CONFIDENCE_BANDS`
- `calculateTraceGridNormalizedConfidence`
- `getTraceGridConfidenceBand`
- `TraceGridCollectionAssessmentOutput`

These are schema-ready primitives only. They are not wired into production collection runs.

## Confidence Calculation Contract

The shared utility follows the MVP formula:

```text
weighted_score = Σ(step_score × step_weight)
max_weighted_score = 5 × 100
normalized_confidence = weighted_score ÷ max_weighted_score
```

The utility is deterministic and side-effect free. It validates that each step score is an integer from `0` to `5`.

## Collection-Agent Output Contract

Future collection-agent outputs should be structured around:

- claim assessed;
- sources examined;
- signals collected;
- noise removed;
- corroborating evidence;
- contradictory evidence;
- relationships identified;
- confidence score;
- confidence rationale;
- collection gaps;
- recommended follow-on collection;
- assessment summary.

The output is a collection assessment. It is not a final analytic conclusion. A collection-agent output must not present a conclusion without a confidence rationale.

## Ecosystem Separation

TraceGrid remains responsible for evidence collection and weighted evidence products.

Axiom Forge remains responsible for fusion, validation, contextualization, gap analysis, confidence reassessment, and validated understanding.

StratSight remains responsible for mission orchestration, confidence sufficiency, decision support, and human-facing decision context.

## Future Integration Order

1. Add non-breaking API schemas for methodology score payloads.
2. Add UI-only methodology and confidence panels using the shared constants.
3. Add database fields or tables for persisted methodology step scores after schema design review.
4. Add provider orchestration interfaces that request capabilities rather than vendors.
5. Connect provider outputs to evidence packages.
6. Only after validation, enable production scoring workflows.

## Explicitly Deferred

- Firecrawl, ScraperAPI, OpenStreetMap, Nominatim, Overpass, H3, PostGIS, Mapbox, and other provider integrations.
- API keys and environment variables for providers.
- Runtime provider classes.
- Production scoring execution.
- Collection-agent runtime behavior changes.
- Database table renames.
- Legacy Paperclip route removal.
