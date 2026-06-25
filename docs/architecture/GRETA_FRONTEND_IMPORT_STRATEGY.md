# Greta Frontend Import Strategy

Status: planning only. Do not import the Greta repository until this strategy is reviewed and approved.

## Source Repositories

- TraceGrid long-term product source of truth: this repository.
- Greta frontend prototype source: `https://github.com/qlconsulting/PROJECT-Build-the-frontend-prototype-for-a-new-in-1896`
- Intended TraceGrid placement for the prototype frontend: `apps/frontend`

## Current TraceGrid Repository Structure

The current repository is a pnpm monorepo inherited from Paperclip:

| Path | Current purpose |
|---|---|
| `server/` | Express API, orchestration services, auth, adapter registry, route modules, and TraceGrid alias/evidence routes. |
| `ui/` | Existing React + Vite board UI package (`@paperclipai/ui`). |
| `cli/` | CLI package and command client. |
| `packages/shared/` | Shared TypeScript constants, API types, validators, TraceGrid terminology, evidence schema, and methodology primitives. |
| `packages/db/` | Drizzle schema, migrations, DB clients, embedded Postgres support. |
| `packages/adapters/*` | Built-in adapter implementations. |
| `packages/adapter-utils/` | Shared adapter runtime utilities. |
| `packages/teams-catalog/` | Bundled collection-cell/team catalog templates. |
| `packages/skills-catalog/` | Bundled skills catalog. |
| `packages/plugins/*` | Plugin SDK, plugin packages, and examples. |
| `doc/` | Product, implementation, database, development, and operational docs. |
| `docs/` | Published documentation site content and TraceGrid architecture/domain docs. |
| `tests/` | E2E and release-smoke tests. |

Current workspace packages are declared in `pnpm-workspace.yaml`:

```yaml
packages:
  - packages/*
  - packages/adapters/*
  - packages/plugins/*
  - "!packages/plugins/sandbox-providers/**"
  - packages/plugins/examples/*
  - "!packages/plugins/examples/plugin-orchestration-smoke-example"
  - server
  - ui
  - cli
```

There is no existing `apps/` workspace package today.

## Greta Repository Inspection Status

The provided repository URL could not be inspected from this environment:

```text
https://github.com/qlconsulting/PROJECT-Build-the-frontend-prototype-for-a-new-in-1896
```

Observed access results:

- `gh repo view qlconsulting/PROJECT-Build-the-frontend-prototype-for-a-new-in-1896` returned repository not found.
- GitHub REST contents lookup returned `404 Not Found`.
- `git ls-remote` returned repository not found.

Because the repository is currently inaccessible to this environment, its framework cannot be confirmed yet. It may be private, renamed, under a different owner, or not shared with the GitHub token available here.

Do not import until the repository can be inspected.

## Framework Detection Procedure Once Access Works

Inspect the Greta repo before import:

1. Read root `package.json`.
2. Check for framework markers:
   - Vite: `vite.config.*`, `index.html`, `src/main.*`, `@vitejs/*`.
   - React: `react`, `react-dom`, JSX/TSX entrypoints.
   - Next.js: `next.config.*`, `app/`, `pages/`, `next` dependency.
   - Remix: `remix.config.*`, `@remix-run/*`.
   - Astro/Svelte/Vue: corresponding config/dependencies.
3. Inspect package manager files:
   - `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`.
4. Inspect build scripts:
   - `dev`, `build`, `preview`, `typecheck`, `lint`, `test`.
5. Inspect environment files without copying secrets:
   - `.env.example` is safe to review.
   - `.env`, `.env.local`, and secret-like files must not be imported.

## Recommended Import Path

Use `apps/frontend` as the isolated Greta prototype package:

```text
apps/
  frontend/
    package.json
    src/
    public/
    ...
```

Rationale:

- Keeps Greta separate from the existing production `ui/` package.
- Avoids overwriting TraceGrid backend, database, API, doctrine, and existing UI files.
- Allows independent build/typecheck stabilization.
- Provides a clear path for Greta to evolve into the future TraceGrid frontend while preserving current Paperclip-derived UI.

## Intended Future Monorepo Structure

```text
apps/
  frontend/        # Greta-generated frontend prototype after approved import
packages/
  shared/          # Existing shared TraceGrid constants, validators, API contracts
  types/           # Future frontend/backend-neutral domain and API DTO types
  ui/              # Future shared TraceGrid UI primitives/design system
docs/              # Architecture, domain language, methodology, import docs
server/            # Existing production backend
ui/                # Existing production/compatibility board UI until migration
cli/               # Existing CLI
```

Recommended package naming after import:

- `apps/frontend`: `@tracegrid/frontend` or private app package name.
- `packages/types`: `@tracegrid/types` after it exists.
- `packages/ui`: `@tracegrid/ui` after it exists.

Do not rename existing `@paperclipai/*` packages in the import step.

## Workspace Update Plan

After import approval, update `pnpm-workspace.yaml` additively:

```yaml
  - apps/*
```

This should be committed with the imported app only after confirming the Greta package manager and scripts.

## Initial Greta ↔ TraceGrid API Contract

This is a frontend-facing contract target, not a backend implementation change.

### Mission Workspaces

Purpose: frontend view of mission-scoped workspaces and operational context.

Fields:

- `id`
- `collectionCellId`
- `name`
- `description`
- `status`
- `areaOfInterest`
- `createdAt`
- `updatedAt`

Likely backing compatibility objects:

- current projects/workspaces;
- future `mission_workspaces` alias.

### Collection Directives

Purpose: high-level collection requirements from Axiom Forge or authorized operators.

Fields:

- `id`
- `collectionCellId`
- `title`
- `description`
- `status`
- `priority`
- `sourceTypesRequested`
- `axiomDirectiveRef`
- `createdAt`
- `updatedAt`

Likely backing compatibility objects:

- current goals;
- TraceGrid collection directive alias routes.

### Collection Agents

Purpose: isolated source-specialized collectors.

Fields:

- `id`
- `collectionCellId`
- `name`
- `role`
- `sourceType`
- `status`
- `providerCapabilities`
- `lastCollectionRunAt`
- `createdAt`
- `updatedAt`

Likely backing compatibility objects:

- current agents with `collectionSourceType`.

### Source Catalog

Purpose: registered evidence sources and retrievable source classes.

Fields:

- `id`
- `collectionCellId`
- `sourceType`
- `name`
- `url`
- `providerCapabilityRequired`
- `trustNotes`
- `status`

Likely backing compatibility objects:

- future additive catalog; no current production table should be renamed.

### Evidence Items

Purpose: atomic evidence records before or within package assembly.

Fields:

- `id`
- `evidencePackageId`
- `sourceType`
- `sourceName`
- `url`
- `title`
- `rawText`
- `retrievedAt`
- `confidence`
- `limitations`

Likely backing compatibility objects:

- current `evidence_packages` rows may act as package-level records until evidence-item granularity exists.

### Evidence Packages

Purpose: normalized packages returned to Axiom Forge.

Fields:

- `id`
- `collectionCellId`
- `collectionJobId`
- `collectionAgentId`
- `sourceType`
- `sourceName`
- `url`
- `title`
- `author`
- `publishedAt`
- `retrievedAt`
- `rawText`
- `mediaUrls`
- `metadata`
- `confidence`
- `limitations`
- `dedupeKey`

Likely backing compatibility objects:

- current `evidence_packages` table and API routes.

### Entities

Purpose: extracted people, organizations, places, infrastructure, events, or topics.

Fields:

- `id`
- `collectionCellId`
- `kind`
- `label`
- `description`
- `sourceEvidenceIds`
- `confidence`
- `metadata`

Likely backing compatibility objects:

- future additive entity extraction layer.

### Relationships

Purpose: mapped relationships between entities, sources, directives, or evidence packages.

Fields:

- `id`
- `collectionCellId`
- `fromEntityId`
- `toEntityId`
- `relationshipType`
- `supportingEvidenceIds`
- `confidence`
- `metadata`

Likely backing compatibility objects:

- future additive relationship layer.

### Confidence Scores

Purpose: Evidence Confidence and Methodological Confidence display.

Fields:

- `id`
- `targetKind`
- `targetId`
- `normalizedConfidence`
- `confidenceBand`
- `methodologyScores`
- `confidenceRationale`
- `updatedAt`

Likely backing compatibility objects:

- current shared methodology constants/types;
- future persisted scoring tables after review.

### Collection Jobs

Purpose: assignable source-specific collection work.

Fields:

- `id`
- `collectionCellId`
- `collectionDirectiveId`
- `title`
- `description`
- `status`
- `priority`
- `sourceType`
- `assigneeCollectionAgentId`
- `createdAt`
- `updatedAt`

Likely backing compatibility objects:

- current issues with `collectionSourceType`.

### Methodology Stages

Purpose: UI panels for Observe/Collect/Filter/Corroborate/Map/Assess/Produce.

Fields:

- `stepId`
- `label`
- `weight`
- `score`
- `rationale`
- `supportingEvidenceIds`

Likely backing compatibility objects:

- shared `TRACEGRID_METHODOLOGY_*` constants;
- future scoring persistence.

### Geospatial Objects

Purpose: location and area-of-interest support for future geospatial collection.

Fields:

- `id`
- `collectionCellId`
- `kind`
- `name`
- `geometry`
- `source`
- `confidence`
- `metadata`

Likely backing compatibility objects:

- future additive geospatial model.
- Do not add H3, PostGIS, Mapbox, OpenStreetMap, Nominatim, or Overpass code during import.

## Greta Frontend Terminology Mapping

| Greta / generic UI concept | TraceGrid term |
|---|---|
| Dashboard | Collection Operations Center |
| Workspace | Mission Workspace |
| Company / Organization | Collection Cell |
| Team | Intelligence Element |
| Agent | Collection Agent |
| Goal | Collection Directive |
| Task / Issue | Collection Job |
| Source | Evidence Source |
| Report / Output | Evidence Package / Weighted Evidence Product |
| Analysis | Collection Assessment |
| Recommendation | Follow-on Collection Recommendation |
| Confidence | Evidence Confidence / Methodological Confidence |
| User | Analyst / Operator, depending on context |

Default rule: use **Collection Cell** for inherited company/tenant wording unless broader distributed structures require Collection Network.

## Import Safety Rules

Do not import:

- `.git/`;
- `.env`, `.env.local`, `.env.*.local`;
- secrets, tokens, API keys, provider credentials;
- generated build outputs (`dist/`, `.next/`, `build/`, `out/`);
- dependency directories (`node_modules/`);
- lockfiles until the package manager plan is confirmed;
- deployment configuration that would overwrite TraceGrid settings.

Do not overwrite:

- root `package.json`;
- root `pnpm-workspace.yaml` except for additive `apps/*` workspace entry after approval;
- existing `ui/`;
- `server/`;
- `packages/db/`;
- `packages/shared/`;
- `doc/` or existing doctrine docs.

## Migration Risks

1. Greta repo is currently inaccessible from this environment; import cannot be safely planned at file-level granularity yet.
2. Framework and package manager are unknown until repo access is fixed.
3. Dependency conflicts may occur with React/Vite/Tailwind versions already used in `ui/`.
4. Adding `apps/*` to pnpm workspaces may alter lockfile resolution.
5. Greta may contain generated assets, local config, or secrets that must be excluded.
6. Greta may assume a mock backend schema that differs from TraceGrid evidence/domain contracts.
7. Duplicate design-system dependencies may appear until `packages/ui` is created.
8. Route names may conflict with current `/api` expectations if Greta assumes standalone hosting.

## Recommended Next Import Sequence

1. Restore access to the Greta repository for this environment.
2. Inspect Greta root files and framework markers.
3. Create a clean import branch from this planning branch or the approved base.
4. Copy Greta into `apps/frontend` only.
5. Exclude secrets, generated outputs, dependencies, and Git metadata.
6. Add `apps/*` to `pnpm-workspace.yaml`.
7. Normalize `apps/frontend/package.json` scripts.
8. Run `pnpm install` only if lockfile policy allows it for the import PR.
9. Run targeted `pnpm --filter <frontend-package> typecheck/build`.
10. Only then consider shared contract imports from `packages/shared`.

## Approval Prompt for Actual Import

Use this exact prompt after Greta repo access is available:

> Approved. Proceed with importing the Greta frontend prototype into `apps/frontend` only. Do not overwrite existing TraceGrid files. Exclude `.git`, `node_modules`, build outputs, local env files, secrets, and unrelated deployment artifacts. Add `apps/*` to `pnpm-workspace.yaml` only if required. Preserve the existing backend, database, API, doctrine, and documentation. After import, run the smallest relevant frontend install/build/typecheck checks and stop for review before wiring production backend APIs.
