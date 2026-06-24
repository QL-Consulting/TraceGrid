import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { EvidencePackageRecord } from "../api/issues";
import { EvidencePackageSection } from "./EvidencePackageSection";

function makeEvidencePackage(overrides: Partial<EvidencePackageRecord> = {}): EvidencePackageRecord {
  return {
    id: "evidence-1",
    company_id: "company-1",
    source_type: "web",
    source_name: "Example Site",
    url: "https://example.com/source",
    title: "Example evidence",
    author: "Reporter",
    published_at: "2026-06-20T10:00:00.000Z",
    retrieved_at: "2026-06-24T12:00:00.000Z",
    raw_text: "This is raw source text collected by TraceGrid. It is evidence, not a final report.",
    media_urls: [],
    metadata: {},
    collection_agent: "Web Agent",
    collection_agent_id: "agent-1",
    collection_job_id: "11111111-1111-4111-8111-111111111111",
    confidence: 0.82,
    limitations: ["Dynamic comments were not loaded."],
    content_hash: "hash",
    dedupe_key: "dedupe",
    duplicate_of_id: null,
    created_at: "2026-06-24T12:00:01.000Z",
    updated_at: "2026-06-24T12:00:01.000Z",
    ...overrides,
  };
}

describe("EvidencePackageSection", () => {
  it("renders Evidence Package metadata and source link", () => {
    const markup = renderToStaticMarkup(
      <EvidencePackageSection evidencePackages={[makeEvidencePackage()]} />,
    );

    expect(markup).toContain("Evidence Packages");
    expect(markup).toContain("Example evidence");
    expect(markup).toContain("Example Site");
    expect(markup).toContain("Reporter");
    expect(markup).toContain("Confidence 82%");
    expect(markup).toContain("Dynamic comments were not loaded.");
    expect(markup).toContain("https://example.com/source");
  });

  it("renders nothing when there are no evidence packages", () => {
    expect(renderToStaticMarkup(<EvidencePackageSection evidencePackages={[]} />)).toBe("");
    expect(renderToStaticMarkup(<EvidencePackageSection evidencePackages={undefined} />)).toBe("");
  });

  it("marks duplicate evidence packages", () => {
    const markup = renderToStaticMarkup(
      <EvidencePackageSection
        evidencePackages={[
          makeEvidencePackage({
            duplicate_of_id: "canonical-evidence",
          }),
        ]}
      />,
    );

    expect(markup).toContain("Duplicate");
  });
});
