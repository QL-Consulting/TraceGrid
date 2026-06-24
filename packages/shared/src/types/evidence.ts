import type { TraceGridSourceType } from "../constants.js";

export interface EvidencePackage {
  source_type: TraceGridSourceType;
  source_name: string;
  url: string;
  title: string;
  author: string | null;
  published_at: string | null;
  retrieved_at: string;
  raw_text: string;
  media_urls: string[];
  metadata: Record<string, unknown>;
  collection_agent: string;
  collection_job_id: string;
  confidence: number;
  limitations: string[];
}
