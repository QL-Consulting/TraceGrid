import { describe, expect, it } from "vitest";
import { evidencePackageSchema } from "./evidence.js";

const validEvidencePackage = {
  source_type: "web",
  source_name: "Example Site",
  url: "https://example.com/source",
  title: "Example source title",
  author: "Example Author",
  published_at: "2026-06-20T10:30:00.000Z",
  retrieved_at: "2026-06-24T12:00:00.000Z",
  raw_text: "Raw collected source text.",
  media_urls: ["https://example.com/image.png"],
  metadata: {
    language: "en",
    retrieval_method: "direct_fetch",
  },
  collection_agent: "Web Agent",
  collection_job_id: "11111111-1111-4111-8111-111111111111",
  confidence: 0.87,
  limitations: ["Robots policy allowed retrieval, but comments were not loaded."],
};

describe("evidencePackageSchema", () => {
  it("accepts a complete TraceGrid evidence package", () => {
    const parsed = evidencePackageSchema.parse(validEvidencePackage);

    expect(parsed.source_type).toBe("web");
    expect(parsed.collection_agent).toBe("Web Agent");
    expect(parsed.confidence).toBe(0.87);
  });

  it("accepts nullable author and published_at when the source omits them", () => {
    const parsed = evidencePackageSchema.parse({
      ...validEvidencePackage,
      author: null,
      published_at: null,
      source_type: "document_pdf",
      media_urls: [],
    });

    expect(parsed.author).toBeNull();
    expect(parsed.published_at).toBeNull();
    expect(parsed.media_urls).toEqual([]);
  });

  it("rejects invalid source type, URLs, datetimes, confidence, and media_urls shape", () => {
    const parsed = evidencePackageSchema.safeParse({
      ...validEvidencePackage,
      source_type: "social_media",
      url: "not-a-url",
      published_at: "June 20, 2026",
      retrieved_at: "not-a-date",
      media_urls: "https://example.com/image.png",
      confidence: 1.5,
    });

    expect(parsed.success).toBe(false);
    if (parsed.success) {
      throw new Error("Expected invalid evidence package");
    }
    expect(parsed.error.issues.map((issue) => issue.path.join("."))).toEqual([
      "source_type",
      "url",
      "published_at",
      "retrieved_at",
      "media_urls",
      "confidence",
    ]);
  });

  it("requires every Evidence Package schema field", () => {
    const parsed = evidencePackageSchema.safeParse({
      source_type: "web",
    });

    expect(parsed.success).toBe(false);
    if (parsed.success) {
      throw new Error("Expected missing evidence package fields");
    }
    expect(parsed.error.issues.map((issue) => issue.path.join("."))).toEqual([
      "source_name",
      "url",
      "title",
      "author",
      "published_at",
      "retrieved_at",
      "raw_text",
      "media_urls",
      "metadata",
      "collection_agent",
      "collection_job_id",
      "confidence",
      "limitations",
    ]);
  });

  it("rejects unknown keys to keep the evidence contract stable", () => {
    const parsed = evidencePackageSchema.safeParse({
      ...validEvidencePackage,
      conclusion: "This is intentionally not part of TraceGrid evidence.",
    });

    expect(parsed.success).toBe(false);
    if (parsed.success) {
      throw new Error("Expected unknown evidence package key rejection");
    }
    expect(parsed.error.issues.map((issue) => issue.code)).toContain("unrecognized_keys");
  });
});
