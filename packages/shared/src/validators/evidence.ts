import { z } from "zod";
import { TRACEGRID_SOURCE_TYPES } from "../constants.js";

const nonEmptyTrimmedString = z.string().trim().min(1);
const nullableNonEmptyString = nonEmptyTrimmedString.nullable();

export const evidencePackageSchema = z
  .object({
    source_type: z.enum(TRACEGRID_SOURCE_TYPES),
    source_name: nonEmptyTrimmedString,
    url: z.string().url(),
    title: nonEmptyTrimmedString,
    author: nullableNonEmptyString,
    published_at: z.string().datetime({ offset: true }).nullable(),
    retrieved_at: z.string().datetime({ offset: true }),
    raw_text: z.string().min(1),
    media_urls: z.array(z.string().url()),
    metadata: z.record(z.string(), z.unknown()),
    collection_agent: nonEmptyTrimmedString,
    collection_job_id: z.string().uuid(),
    confidence: z.number().min(0).max(1),
    limitations: z.array(nonEmptyTrimmedString),
  })
  .strict();

export type EvidencePackageInput = z.infer<typeof evidencePackageSchema>;
