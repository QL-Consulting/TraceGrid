# TraceGrid UX Terminology Mapping

Backend names remain conservative for compatibility. Product-facing labels should use TraceGrid doctrine while legacy Paperclip identifiers remain available until explicitly migrated.

| Legacy Paperclip Term | TraceGrid Canonical Term | UI Label Recommendation | Backend Rename Status | Notes |
|---|---|---|---|---|
| Company | Collection Cell | Collection Cell | Alias now / rename later | Collection Network remains compatibility/higher-level grouping. |
| Companies | Collection Cells | Collection Cells | Alias now / rename later | Do not rename `companies` table yet. |
| Agent | Collection Agent | Collection Agent | Alias now / rename later | Existing `agents` schema remains. |
| Agents | Collection Agents | Collection Agents | Alias now / rename later | Source type fields are additive. |
| Goal | Collection Directive | Collection Directive | Alias now / rename later | Existing goals remain compatibility internals. |
| Goals | Collection Directives | Collection Directives | Alias now / rename later | Axiom-facing directive aliases are additive. |
| Issue | Collection Job | Collection Job | Alias now / rename later | Existing issues remain compatibility internals. |
| Issues | Collection Jobs | Collection Jobs | Alias now / rename later | Do not remove existing issue routes. |
| Report | Evidence Package | Evidence Package | Preserve for compatibility | Avoid final-report wording in TraceGrid UI. |
| Reports | Evidence Packages | Evidence Packages | Preserve for compatibility | Evidence Packages are durable outputs. |
| Workspace | Mission Workspace | Mission Workspace | Preserve for compatibility | Workspace code remains unchanged. |
| Task | Collection Task | Collection Task | Preserve for compatibility | Use Collection Job for primary issue-level UI. |
| Source | Evidence Source | Evidence Source | UI-only now | Source type constants are additive. |
| Dashboard | Collection Operations Center | Collection Operations Center | UI-only now | Route can remain `/dashboard`. |
| Project | Collection Mission | Collection Mission | Future migration required | Existing projects are still compatibility grouping/workspace records. |
| Team | Intelligence Element | Intelligence Element | Preserve for compatibility | Catalog/team internals remain. |
| User | Analyst / Operator | Operator or Analyst | UI-only now | Choose by context. |
| Customer | Mission Stakeholder | Mission Stakeholder | UI-only now | Avoid business-sales framing. |
| Business Objective | Collection Requirement | Collection Requirement | UI-only now | Product docs should avoid business framing. |
| Business Context | Operational Context | Operational Context | UI-only now | Use for mission context. |
| Insight | Evidence Finding | Evidence Finding | UI-only now | Avoid implying final analysis. |
| Analysis | Collection Assessment | Collection Assessment | UI-only now | Use Analysis only for Axiom Forge. |
| Recommendation | Follow-on Collection Recommendation | Follow-on Collection Recommendation | UI-only now | Final recommendations belong downstream. |
| Status | Collection Status | Collection Status | Preserve for compatibility | Schema enum names remain. |
| Priority | Collection Priority | Collection Priority | Preserve for compatibility | Schema enum names remain. |
| Confidence | Evidence Confidence / Methodological Confidence | Evidence Confidence | Alias now / rename later | Shared methodology constants are additive. |
