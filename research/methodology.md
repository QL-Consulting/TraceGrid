# TraceGrid Case-Study Methodology

Generated: 2026-06-24T21:30:46Z

## Purpose

This research artifact builds a large, auditable first-pass corpus for estimating how much integrity damage occurs when steps in a shared epistemological workflow are weak, skipped, delayed, or corrupted:

1. Observe Digital Environment
2. Collect Signals
3. Filter Noise
4. Corroborate
5. Map Relationships
6. Assess Confidence
7. Produce Understanding

## Corpus construction

The dataset contains one row per source-linked real-world case. Each profession has at least 1,000 rows:

| Profession | Rows |
| --- | --- |
| OSINT Intelligence Analyst | 1000 |
| OSINT Investigative Journalist | 1000 |
| Cyber Threat Intelligence Analyst | 1000 |
| Meteorologist / Weather Forecaster | 1000 |
| Quantitative Trader / Market Analyst | 1000 |
| Competitive Intelligence Analyst | 1000 |

## Source strategy

- **OSINT Intelligence Analyst:** GDELT 2.0 event records, where each event is coded from online news/open sources and includes a source URL, actors, geography, event code, mention count, source count, article count, tone, and date fields.
- **OSINT Investigative Journalist:** Bellingcat public article sitemap entries, with ICIJ configured as a fallback source if sitemap volume changes. Coding is based on URL/date/slug metadata, with higher confidence for slugs indicating debunking, geolocation, leaked-record, or conflict-investigation cases.
- **Cyber Threat Intelligence Analyst:** CISA Known Exploited Vulnerabilities catalog, linked to NVD CVE pages and CISA KEV documentation.
- **Meteorologist / Weather Forecaster:** NOAA/NCEI Storm Events details, including event type, location, reporting source, casualty and damage fields, and narratives where present.
- **Quantitative Trader / Market Analyst:** Yahoo Finance chart data for S&P 500 daily sessions; cases are daily signal/outcome observations.
- **Competitive Intelligence Analyst:** SEC EDGAR submissions and filing archive URLs for major public-company filings.

## Coding model

Each workflow step receives:

- `*_status`: present, weak, failed, or skipped/catastrophically failed.
- `*_impact_score`: 0 to 4, where 0 means no observed/proxy evidence of integrity impact and 4 means catastrophic impact.
- `*_failure_type`: input, validation, interpretation, confidence, or communication failure.
- `*_degradation`: textual severity.

Scores are proxy-coded from structured public metadata rather than from full manual expert memos. This is appropriate for first-pass scale calibration and for discovering candidate weights, but the row-level `confidence_in_case_coding` column should be used when selecting cases for expert re-review.

## Weight calculation

For each step, the generator computes:

- Average impact score
- Median impact score
- Failure frequency
- Catastrophic failure frequency
- Failure count
- Catastrophic count

The normalized importance raw score is:

`average_impact * 0.55 + median_impact * 0.25 + failure_frequency * 1.25 + catastrophic_frequency * 1.75`

The raw scores are normalized to 100% globally and within each profession. This formula intentionally rewards repeated failures and catastrophic-tail risk while still preserving average observed damage.

## Limitations and safeguards

- The corpus is source-linked and real-world, but most rows are not manually full-text coded.
- Some professions have direct failure evidence (for example market reversals, casualties/damage, known exploitation); others use metadata proxies for where integrity would collapse if a workflow step were weak.
- The resulting weights should guide architecture priorities and expert sampling, not be treated as immutable ground truth.
- Rows include confidence labels so TraceGrid can later prioritize low-confidence/high-impact cases for human audit.
