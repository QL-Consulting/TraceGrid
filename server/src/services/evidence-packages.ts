import { createHash } from "node:crypto";
import { and, desc, eq, isNull } from "drizzle-orm";
import type { Db } from "@paperclipai/db";
import { agents, evidencePackages, issues } from "@paperclipai/db";
import type { EvidencePackage } from "@paperclipai/shared";
import { evidencePackageSchema } from "@paperclipai/shared";
import { conflict, notFound, unprocessable } from "../errors.js";

type EvidencePackageRow = typeof evidencePackages.$inferSelect;
type EvidencePackageInsert = typeof evidencePackages.$inferInsert;

export interface EvidencePackageReadModel extends EvidencePackage {
  id: string;
  company_id: string;
  collection_agent_id: string;
  content_hash: string;
  dedupe_key: string;
  duplicate_of_id: string | null;
  created_at: string;
  updated_at: string;
}

function normalizeUrlForDedupe(input: string) {
  const url = new URL(input);
  url.hash = "";
  url.hostname = url.hostname.toLowerCase();
  if (
    (url.protocol === "https:" && url.port === "443") ||
    (url.protocol === "http:" && url.port === "80")
  ) {
    url.port = "";
  }
  return url.toString();
}

function normalizeRawTextForHash(input: string) {
  return input.replace(/\s+/g, " ").trim();
}

function sha256(input: string) {
  return createHash("sha256").update(input).digest("hex");
}

function buildContentHash(rawText: string) {
  return sha256(normalizeRawTextForHash(rawText));
}

function buildDedupeKey(input: { sourceType: string; url: string; contentHash: string }) {
  return sha256([
    input.sourceType,
    normalizeUrlForDedupe(input.url),
    input.contentHash,
  ].join("\n"));
}

function dateToIso(value: Date | string | null) {
  if (value === null) return null;
  return (value instanceof Date ? value : new Date(value)).toISOString();
}

function toReadModel(row: EvidencePackageRow): EvidencePackageReadModel {
  return {
    id: row.id,
    company_id: row.companyId,
    source_type: row.sourceType as EvidencePackage["source_type"],
    source_name: row.sourceName,
    url: row.url,
    title: row.title,
    author: row.author ?? null,
    published_at: dateToIso(row.publishedAt),
    retrieved_at: dateToIso(row.retrievedAt)!,
    raw_text: row.rawText,
    media_urls: row.mediaUrls,
    metadata: row.metadata,
    collection_agent: row.collectionAgent,
    collection_agent_id: row.collectionAgentId,
    collection_job_id: row.collectionJobId,
    confidence: row.confidence,
    limitations: row.limitations,
    content_hash: row.contentHash,
    dedupe_key: row.dedupeKey,
    duplicate_of_id: row.duplicateOfId ?? null,
    created_at: row.createdAt.toISOString(),
    updated_at: row.updatedAt.toISOString(),
  };
}

function parseEvidenceDates(input: EvidencePackage) {
  return {
    publishedAt: input.published_at ? new Date(input.published_at) : null,
    retrievedAt: new Date(input.retrieved_at),
  };
}

export function evidencePackageService(db: Db) {
  async function getCollectionJob(companyId: string, collectionJobId: string) {
    return db
      .select({
        id: issues.id,
        companyId: issues.companyId,
        collectionSourceType: issues.collectionSourceType,
      })
      .from(issues)
      .where(and(eq(issues.id, collectionJobId), eq(issues.companyId, companyId)))
      .then((rows) => rows[0] ?? null);
  }

  async function getCollectionAgent(companyId: string, collectionAgentId: string) {
    return db
      .select({
        id: agents.id,
        companyId: agents.companyId,
        name: agents.name,
        collectionSourceType: agents.collectionSourceType,
      })
      .from(agents)
      .where(and(eq(agents.id, collectionAgentId), eq(agents.companyId, companyId)))
      .then((rows) => rows[0] ?? null);
  }

  return {
    listForCollectionJob: async (companyId: string, collectionJobId: string) => {
      const rows = await db
        .select()
        .from(evidencePackages)
        .where(and(
          eq(evidencePackages.companyId, companyId),
          eq(evidencePackages.collectionJobId, collectionJobId),
        ))
        .orderBy(desc(evidencePackages.createdAt));
      return rows.map(toReadModel);
    },

    getById: async (id: string) => {
      const row = await db
        .select()
        .from(evidencePackages)
        .where(eq(evidencePackages.id, id))
        .then((rows) => rows[0] ?? null);
      return row ? toReadModel(row) : null;
    },

    createForCollectionJob: async (input: {
      companyId: string;
      collectionJobId: string;
      collectionAgentId: string;
      evidence: unknown;
    }) => {
      const evidence = evidencePackageSchema.parse(input.evidence);
      if (evidence.collection_job_id !== input.collectionJobId) {
        throw unprocessable("Evidence collection_job_id must match the collection job route");
      }

      const [job, agent] = await Promise.all([
        getCollectionJob(input.companyId, input.collectionJobId),
        getCollectionAgent(input.companyId, input.collectionAgentId),
      ]);
      if (!job) throw notFound("Collection job not found");
      if (!agent) throw notFound("Collection agent not found");
      if (job.collectionSourceType && job.collectionSourceType !== evidence.source_type) {
        throw unprocessable("Evidence source_type does not match the collection job source type");
      }
      if (agent.collectionSourceType && agent.collectionSourceType !== evidence.source_type) {
        throw conflict("Evidence source_type does not match the collection agent source type");
      }

      const dates = parseEvidenceDates(evidence);
      const contentHash = buildContentHash(evidence.raw_text);
      const dedupeKey = buildDedupeKey({
        sourceType: evidence.source_type,
        url: evidence.url,
        contentHash,
      });
      const canonical = await db
        .select({ id: evidencePackages.id })
        .from(evidencePackages)
        .where(and(
          eq(evidencePackages.companyId, input.companyId),
          eq(evidencePackages.dedupeKey, dedupeKey),
          isNull(evidencePackages.duplicateOfId),
        ))
        .then((rows) => rows[0] ?? null);

      const values: EvidencePackageInsert = {
        companyId: input.companyId,
        collectionJobId: input.collectionJobId,
        collectionAgentId: input.collectionAgentId,
        sourceType: evidence.source_type,
        sourceName: evidence.source_name,
        url: evidence.url,
        title: evidence.title,
        author: evidence.author,
        publishedAt: dates.publishedAt,
        retrievedAt: dates.retrievedAt,
        rawText: evidence.raw_text,
        mediaUrls: evidence.media_urls,
        metadata: evidence.metadata,
        collectionAgent: evidence.collection_agent,
        confidence: evidence.confidence,
        limitations: evidence.limitations,
        contentHash,
        dedupeKey,
        duplicateOfId: canonical?.id ?? null,
      };

      const row = await db
        .insert(evidencePackages)
        .values(values)
        .returning()
        .then((rows) => rows[0] ?? null);
      if (!row) throw unprocessable("Evidence package could not be created");
      return toReadModel(row);
    },
  };
}

export const evidencePackageInternals = {
  buildContentHash,
  buildDedupeKey,
  normalizeUrlForDedupe,
};
