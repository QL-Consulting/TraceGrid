---
name: TraceGrid Core Collection Network
description: Source-specialized TraceGrid collection network with one coordinator and five isolated collection agents for web, news/RSS, Reddit/forum, YouTube/transcript, and document/PDF evidence retrieval.
schema: agentcompanies/v1
slug: tracegrid-core
category: source-collection
key: paperclipai/bundled/source-collection/tracegrid-core
manager: agents/tracegrid-coordinator/AGENTS.md
includes:
  - agents/web-agent/AGENTS.md
  - agents/news-rss-agent/AGENTS.md
  - agents/reddit-forum-agent/AGENTS.md
  - agents/youtube-transcript-agent/AGENTS.md
  - agents/document-pdf-agent/AGENTS.md
defaultInstall: true
recommendedForCompanyTypes:
  - intelligence
  - collection
  - research
  - evidence
tags:
  - tracegrid
  - collection
  - evidence
  - source-specialized
---

# TraceGrid Core Collection Network

This bundled network is the default TraceGrid operating shape.

TraceGrid receives collection directives from Axiom Forge, decomposes them into source-specific collection jobs, assigns each job to exactly one source-specialized collection agent, normalizes and deduplicates returned evidence, and packages the evidence back to Axiom Forge.

## Agents

- `TraceGrid Coordinator` — decomposes directives into source-specific collection jobs and packages normalized evidence back to Axiom Forge.
- `Web Agent` — collects from general web pages only.
- `News/RSS Agent` — collects from news sites and RSS/Atom feeds only.
- `Reddit/Forum Agent` — collects from Reddit-style and forum-style discussion sources only.
- `YouTube/Transcript Agent` — collects YouTube metadata and transcripts only.
- `Document/PDF Agent` — collects document and PDF text/metadata only.

## Hard boundaries

- Collection agents do not communicate with each other.
- Collection agents do not synthesize final reports.
- Collection agents do not make analytical judgments, recommendations, or conclusions.
- TraceGrid does not communicate directly with human end users.
- Axiom Forge is the only system allowed to interpret or synthesize collected evidence.
