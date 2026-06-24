# TraceGrid Provider Framework

TraceGrid providers are infrastructure. They do not reason, determine confidence, or produce conclusions.

Providers support portions of the TraceGrid epistemological workflow by acquiring, extracting, enriching, or preparing evidence inputs for Collection Agents and the Provider Orchestration Layer.

## Core Principle

Collection Agents request capabilities, not vendors.

```text
Collection Agent
  ↓
Provider Orchestration Layer
  ↓
Selected Provider
  ↓
Evidence Package / Weighted Evidence Product
```

The Provider Orchestration Layer selects the appropriate provider for a requested capability. This prevents vendor lock-in and keeps Collection Agent logic independent of provider-specific SDKs, credentials, rate limits, and operational quirks.

## Provider Rules

Providers must not:

- determine truth;
- determine final confidence;
- produce final conclusions;
- synthesize human-facing reports;
- bypass TraceGrid evidence packaging;
- communicate directly with Collection Agents through vendor-specific control flow.

Providers may:

- retrieve evidence sources;
- extract source content;
- enrich source metadata;
- normalize provider-specific payloads into TraceGrid-compatible evidence inputs;
- support selected steps of the TraceGrid methodology.

## Initial Provider Classes

### Web Collection Providers

Purpose: structured website retrieval and content extraction.

Initial candidate provider: Firecrawl.

Capabilities:

- website crawling;
- structured webpage extraction;
- Markdown generation;
- metadata extraction;
- document-like webpage ingestion.

Workflow support:

- Observe Environment;
- Collect Signals.

### Web Retrieval Providers

Purpose: resilient access to webpages that require additional retrieval support.

Initial candidate provider: ScraperAPI.

Capabilities:

- anti-bot handling;
- proxy routing;
- geographic routing;
- dynamic page retrieval;
- reliable page acquisition.

Workflow support:

- Observe Environment;
- Collect Signals.

### Geospatial Intelligence Providers

Purpose: geographic enrichment, infrastructure context, location resolution, and future hotspot analysis.

Initial candidate provider stack:

- OpenStreetMap;
- Nominatim;
- Overpass API.

Capabilities:

- geocoding;
- reverse geocoding;
- infrastructure discovery;
- administrative boundaries;
- geographic enrichment;
- environmental context;
- nearby feature discovery.

Workflow support:

- Observe Environment;
- Collect Signals;
- Map Relationships.

Future geospatial capabilities:

- H3 spatial indexing;
- PostGIS spatial analytics;
- Mapbox visualization;
- Kepler.gl / Deck.gl analyst visualization;
- ArcGIS enterprise capability.

## Capability Request Examples

| Collection Agent Request | Provider Orchestrator May Select |
|---|---|
| Structured webpage extraction | Firecrawl |
| Resilient webpage retrieval | ScraperAPI |
| Geographic enrichment | OpenStreetMap / Nominatim / Overpass |

## Implementation Boundary

This document is architecture only. It does not add provider SDKs, API keys, environment variables, runtime provider classes, scraping clients, geospatial clients, or production provider orchestration.
