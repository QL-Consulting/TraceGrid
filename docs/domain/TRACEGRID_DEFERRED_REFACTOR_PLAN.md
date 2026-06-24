# TraceGrid Deferred Refactor Plan

TraceGrid domain-language changes should remain non-breaking until the compatibility surface is stable.

## Phase A: Documentation and Terminology Foundation

- Establish canonical domain language.
- Document UX label guidance.
- Document methodology doctrine.
- Add additive shared constants and aliases where safe.

## Phase B: UI Label / Constants Replacement

- Replace product-facing labels with TraceGrid terms.
- Keep route paths and data contracts stable.
- Prefer shared label maps for new Greta surfaces.

## Phase C: API Alias Layer

- Add TraceGrid route aliases.
- Preserve legacy Paperclip routes.
- Document compatibility status and eventual migration windows.

## Phase D: Internal Type Aliasing

- Add non-breaking type aliases for Collection Cell, Collection Agent, Collection Directive, Collection Job, and Evidence Package.
- Avoid moving tables or changing persisted identifiers.

## Phase E: Database Rename / Migration Only After Stability

- Design migrations after API aliases, UI labels, and downstream integrations are stable.
- Provide backfills, compatibility views, or transitional aliases as needed.

## Phase F: Deprecation of Legacy Paperclip Naming

- Deprecate legacy names only after operators and integrations have migrated.
- Publish migration notes before removal.

## Do Not Rename Yet

- database table names;
- existing route paths;
- existing authentication assumptions;
- legacy Paperclip compatibility aliases;
- production-facing identifiers.

## Future Candidate Renames

- `companies` → `collection_cells`
- `agents` → `collection_agents`
- `goals` → `collection_directives`
- `issues` → `collection_jobs`
- `reports` / work products → `evidence_packages`

## Current Safety Rule

Add aliases. Add label maps. Add documentation references. Do not remove legacy identifiers until a dedicated migration phase is approved.
