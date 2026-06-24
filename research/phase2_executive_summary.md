# Phase II Executive Summary

Generated: 2026-06-24T22:08:37Z

## Corpus used

Phase II used the existing Phase I corpus only: 6,000 rows from `case_studies.csv`. The dataset was not regenerated.

| Profession | Rows |
| --- | --- |
| OSINT Intelligence Analyst | 1000 |
| OSINT Investigative Journalist | 1000 |
| Cyber Threat Intelligence Analyst | 1000 |
| Meteorologist / Weather Forecaster | 1000 |
| Quantitative Trader / Market Analyst | 1000 |
| Competitive Intelligence Analyst | 1000 |

| Source catalog | Rows |
| --- | --- |
| GDELT 2.0 Events bulk export | 1000 |
| Bellingcat public article sitemaps | 1000 |
| CISA Known Exploited Vulnerabilities Catalog | 1000 |
| NOAA/NCEI Storm Events Database 2024 details | 1000 |
| Yahoo Finance chart API for S&P 500 historical daily data | 1000 |
| SEC EDGAR submissions API and filing archives | 1000 |

## Direct answers

1. **Most important global workflow step:** Collect Signals (19.39% final Phase II weight).
2. **Least recoverable step:** Collect Signals (Rarely Recoverable, score 3.229).
3. **Largest catastrophic failures:** Collect Signals (catastrophic frequency 0.0047; average impact 1.249).
4. **Step varying most by modality:** Filter Noise (std dev 4.35 percentage points).
5. **Most universal step by modality:** Collect Signals (lowest std dev 1.41 percentage points).
6. **Weighting TraceGrid should use:**

| Workflow step | Final weight % |
| --- | --- |
| Observe Digital Environment | 13.32 |
| Collect Signals | 19.39 |
| Filter Noise | 10.77 |
| Corroborate | 17.37 |
| Map Relationships | 14.65 |
| Assess Confidence | 17.89 |
| Produce Understanding | 6.61 |

7. **Weighting each collection agent should use:** see `modality_weighting.md`; summarized below by each agent's top three controls.

| Agent | Top workflow controls |
| --- | --- |
| Web Search Agent | Collect Signals (19.69%); Corroborate (19.26%); Assess Confidence (19.17%) |
| News Agent | Corroborate (20.8%); Collect Signals (20.51%); Assess Confidence (19.24%) |
| Social Media Agent | Corroborate (19.5%); Filter Noise (18.7%); Assess Confidence (18.09%) |
| Public Records Agent | Map Relationships (18.12%); Observe Digital Environment (17.28%); Collect Signals (17.09%) |
| Academic / Research Agent | Corroborate (19.77%); Assess Confidence (18.72%); Collect Signals (17.09%) |
| Video / Media Agent | Corroborate (20.5%); Collect Signals (18.12%); Assess Confidence (16.21%) |
| Forum Agent | Filter Noise (19.74%); Corroborate (17.99%); Collect Signals (17.19%) |
| Geospatial / Imagery Agent | Collect Signals (18.97%); Map Relationships (17.52%); Observe Digital Environment (16.3%) |

8. **How Axiom Forge should fuse modality outputs:** use mission-specific trust priors, not a single universal modality ranking. Highest-weight modalities by mission:

| Mission | Top modality trust priors |
| --- | --- |
| General Intelligence | News Agent (15.07%); Web Search Agent (13.48%); Public Records Agent (12.57%) |
| Influence Operations | Social Media Agent (18.05%); News Agent (15.53%); Video / Media Agent (15.44%) |
| Information Warfare | Social Media Agent (16.59%); News Agent (15.16%); Video / Media Agent (14.9%) |
| Competitive Intelligence | Public Records Agent (16.61%); Geospatial / Imagery Agent (15.05%); Academic / Research Agent (14.07%) |
| National Security Monitoring | News Agent (14.17%); Geospatial / Imagery Agent (13.47%); Video / Media Agent (13.07%) |
| Crisis Monitoring | News Agent (15.32%); Social Media Agent (14.5%); Video / Media Agent (14.1%) |
| Strategic Warning | Public Records Agent (14.65%); Geospatial / Imagery Agent (14.44%); News Agent (13.56%) |

9. **Architectural implications:**

- Build an evidence/provenance substrate before optimizing dashboards.
- Treat collection completeness as a hard dependency; absent signals are rarely recoverable.
- Make confidence assessment a first-class, versioned object rather than a prose afterthought.
- Build corroboration and contradiction detection as core services.
- Maintain relationship graphs as operational state, not optional visualization.
- Give each modality its own noise/corroboration/confidence policy.
- Make Axiom Forge fusion mission-aware and uncertainty-preserving.
- Hand StratSight evidence bundles with provenance, graph slice, confidence, contradiction state, and decision thresholds.

10. **MVP priorities:**

1. Source/evidence capture with immutable provenance
2. Collection completeness and coverage tracking
3. Corroboration/contradiction engine
4. Confidence scoring and calibration ledger
5. Relationship graph/entity resolution
6. Modality-specific filtering profiles
7. Axiom Forge fusion matrix and StratSight handoff schema
8. Analyst explanation layer

## Doctrine validation

> TraceGrid is not fundamentally an OSINT platform. TraceGrid is infrastructure for transforming uncertainty into defensible confidence through a structured epistemological workflow.

**Assessment: supported, with limits.**

The evidence supports the doctrine because the strongest Phase II architecture weights do not merely reward finding more online sources. The final model prioritizes collection integrity, confidence assessment, corroboration, and relationship mapping: the functions that turn uncertain observations into claims that can survive audit and decision handoff. The modality analysis also supports the doctrine: news, social, public records, forums, imagery, and academic material require different collection policies, but they converge on the same epistemological controls.

The falsification attempt is important: if TraceGrid were simply an OSINT platform, source discovery and collection volume would dominate. They do not. Collection remains high because missing evidence is least recoverable, but standalone observation/discovery and final report production are not sufficient. The architecture must preserve provenance, expose uncertainty, and fuse contradictory evidence.

The doctrine is not proven as a universal law. The Phase I corpus is proxy-coded, not expert-adjudicated; social, forum, academic, video, and geospatial modality weights are partly inferred; and recovery is counterfactual. Human adjudication is required before treating the numeric weights as stable production defaults. Still, for architectural prioritization, the doctrine is more defensible than an OSINT-platform framing.

## Observed vs inferred findings

- **Observed from corpus:** impact averages, medians, standard deviations, failure frequencies, major/catastrophic frequencies, profession rankings.
- **Inferred from observed corpus plus workflow priors:** recoverability scores and final composite weighting.
- **Inferred for architecture:** modality-specific agent weights and Axiom Forge fusion trust matrix.

## Limitations requiring human adjudication

- Phase I rows are real and cited but mostly proxy-coded from metadata.
- Failure scores and final-output quality are not independent variables.
- Recoverability is not directly observed; it should be tested with expert counterfactual review.
- Social media, forums, academic research, video/media, and geospatial agents need dedicated native corpora.
- Mission-specific fusion weights should be calibrated against real Axiom Forge task outcomes.
