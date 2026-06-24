import { ExternalLink, PackageCheck } from "lucide-react";
import type { EvidencePackageRecord } from "../api/issues";
import { relativeTime } from "../lib/utils";

interface EvidencePackageSectionProps {
  evidencePackages: EvidencePackageRecord[] | null | undefined;
}

function formatSourceType(sourceType: string) {
  return sourceType
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" / ");
}

function formatConfidence(confidence: number) {
  return `${Math.round(confidence * 100)}%`;
}

function excerpt(rawText: string) {
  const normalized = rawText.replace(/\s+/g, " ").trim();
  if (normalized.length <= 220) return normalized;
  return `${normalized.slice(0, 217).trimEnd()}...`;
}

export function EvidencePackageSection({ evidencePackages }: EvidencePackageSectionProps) {
  const packages = evidencePackages ?? [];
  if (packages.length === 0) return null;

  return (
    <section className="space-y-3" aria-label="Evidence Packages">
      <div className="flex items-center gap-2">
        <PackageCheck className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
        <h3 className="text-sm font-medium text-muted-foreground">Evidence Packages</h3>
        <span className="text-xs text-muted-foreground">{packages.length}</span>
      </div>

      <div className="space-y-2">
        {packages.map((item) => (
          <article key={item.id} id={`evidence-package-${item.id}`} className="scroll-mt-20 rounded-lg border border-border p-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-border px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                    {formatSourceType(item.source_type)}
                  </span>
                  {item.duplicate_of_id ? (
                    <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:text-amber-300">
                      Duplicate
                    </span>
                  ) : null}
                  <span className="text-[11px] text-muted-foreground">
                    Confidence {formatConfidence(item.confidence)}
                  </span>
                </div>
                <h4 className="truncate text-sm font-medium">{item.title}</h4>
                <p className="text-xs text-muted-foreground">
                  {item.source_name}
                  {item.author ? ` · ${item.author}` : ""}
                  {" · "}Retrieved {relativeTime(item.retrieved_at)}
                </p>
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex shrink-0 items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
              >
                Open source
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>

            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{excerpt(item.raw_text)}</p>

            {item.limitations.length > 0 ? (
              <div className="mt-3 rounded-md bg-muted/40 px-2 py-1.5">
                <p className="text-[11px] font-medium text-muted-foreground">Limitations</p>
                <ul className="mt-1 list-disc space-y-0.5 pl-4 text-xs text-muted-foreground">
                  {item.limitations.map((limitation, index) => (
                    <li key={`${item.id}-limitation-${index}`}>{limitation}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
