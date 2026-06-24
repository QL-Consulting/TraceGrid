# Phase II Study E: Axiom Forge Fusion Trust Matrix

Generated: 2026-06-24T22:08:37Z

## Status of this analysis

Inferred Conductor-operations model. The matrix normalizes trust allocation across modalities for each mission condition. It combines modality capability attributes with each modality's workflow burden, including a trust penalty for high noise-filtering dependency.

## Fusion trust matrix

| Modality | General Intelligence | Influence Operations | Information Warfare | Competitive Intelligence | National Security Monitoring | Crisis Monitoring | Strategic Warning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Web Search Agent | 13.48 | 11.07 | 11.34 | 11.46 | 11.54 | 11.82 | 11.29 |
| News Agent | 15.07 | 15.53 | 15.16 | 13.21 | 14.17 | 15.32 | 13.56 |
| Social Media Agent | 11.98 | 18.05 | 16.59 | 9.1 | 12.58 | 14.5 | 10.86 |
| Public Records Agent | 12.57 | 8.13 | 9.18 | 16.61 | 12.75 | 10.33 | 14.65 |
| Academic / Research Agent | 11.33 | 7.66 | 8.3 | 14.07 | 10.73 | 8.74 | 12.31 |
| Video / Media Agent | 11.96 | 15.44 | 14.9 | 10.79 | 13.07 | 14.1 | 12.0 |
| Forum Agent | 11.12 | 14.15 | 13.7 | 9.71 | 11.69 | 12.18 | 10.89 |
| Geospatial / Imagery Agent | 12.49 | 9.97 | 10.83 | 15.05 | 13.47 | 13.01 | 14.44 |

Each mission column sums to 100%. These are not source-truth probabilities; they are orchestration priors for how Axiom Forge should allocate attention, contradiction checks, and confidence mass before case-specific evidence is evaluated.

## Fusion guidance

- **General Intelligence:** start broad; use web/news for coverage, then public records, academic, and geospatial for stabilization.
- **Influence Operations:** social, video/media, forums, and news deserve higher attention, but never high standalone trust without corroboration.
- **Information Warfare:** treat social/forum/media as high-signal but adversarial; fuse with news and geospatial for grounding.
- **Competitive Intelligence:** public records should anchor trust; news/web search provide timeliness and context.
- **National Security Monitoring:** geospatial, news, public records, and forums/social should be fused with explicit contradiction tracking.
- **Crisis Monitoring:** timeliness dominates early; news/social/geospatial/video should be weighted heavily but confidence should remain provisional.
- **Strategic Warning:** public records, geospatial, academic/research, forums, and news provide complementary slow/early indicators.

## StratSight handoff requirement

Axiom Forge should hand StratSight not only fused conclusions but also per-modality confidence, contradiction state, provenance coverage, and which modality would most change the estimate if updated.
