import { sql } from "drizzle-orm";
import {
  type AnyPgColumn,
  index,
  jsonb,
  pgTable,
  real,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";
import { agents } from "./agents.js";
import { companies } from "./companies.js";
import { issues } from "./issues.js";

export const evidencePackages = pgTable(
  "evidence_packages",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    companyId: uuid("company_id").notNull().references(() => companies.id),
    collectionJobId: uuid("collection_job_id")
      .notNull()
      .references(() => issues.id, { onDelete: "cascade" }),
    collectionAgentId: uuid("collection_agent_id")
      .notNull()
      .references(() => agents.id, { onDelete: "restrict" }),
    sourceType: text("source_type").notNull(),
    sourceName: text("source_name").notNull(),
    url: text("url").notNull(),
    title: text("title").notNull(),
    author: text("author"),
    publishedAt: timestamp("published_at", { withTimezone: true }),
    retrievedAt: timestamp("retrieved_at", { withTimezone: true }).notNull(),
    rawText: text("raw_text").notNull(),
    mediaUrls: jsonb("media_urls").$type<string[]>().notNull().default([]),
    metadata: jsonb("metadata").$type<Record<string, unknown>>().notNull().default({}),
    collectionAgent: text("collection_agent").notNull(),
    confidence: real("confidence").notNull(),
    limitations: text("limitations").array().notNull().default([]),
    contentHash: text("content_hash").notNull(),
    dedupeKey: text("dedupe_key").notNull(),
    duplicateOfId: uuid("duplicate_of_id").references((): AnyPgColumn => evidencePackages.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => ({
    companyJobIdx: index("evidence_packages_company_job_idx").on(
      table.companyId,
      table.collectionJobId,
    ),
    companyAgentIdx: index("evidence_packages_company_agent_idx").on(
      table.companyId,
      table.collectionAgentId,
    ),
    companySourceTypeIdx: index("evidence_packages_company_source_type_idx").on(
      table.companyId,
      table.sourceType,
    ),
    companyDuplicateOfIdx: index("evidence_packages_company_duplicate_of_idx").on(
      table.companyId,
      table.duplicateOfId,
    ),
    canonicalDedupeUq: uniqueIndex("evidence_packages_company_canonical_dedupe_uq")
      .on(table.companyId, table.dedupeKey)
      .where(sql`${table.duplicateOfId} is null`),
  }),
);
