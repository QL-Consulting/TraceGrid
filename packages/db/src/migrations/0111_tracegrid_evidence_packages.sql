ALTER TABLE "agents" ADD COLUMN "collection_source_type" text;--> statement-breakpoint
ALTER TABLE "issues" ADD COLUMN "collection_source_type" text;--> statement-breakpoint
CREATE TABLE "evidence_packages" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"company_id" uuid NOT NULL,
	"collection_job_id" uuid NOT NULL,
	"collection_agent_id" uuid NOT NULL,
	"source_type" text NOT NULL,
	"source_name" text NOT NULL,
	"url" text NOT NULL,
	"title" text NOT NULL,
	"author" text,
	"published_at" timestamp with time zone,
	"retrieved_at" timestamp with time zone NOT NULL,
	"raw_text" text NOT NULL,
	"media_urls" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"collection_agent" text NOT NULL,
	"confidence" real NOT NULL,
	"limitations" text[] DEFAULT '{}'::text[] NOT NULL,
	"content_hash" text NOT NULL,
	"dedupe_key" text NOT NULL,
	"duplicate_of_id" uuid,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "evidence_packages" ADD CONSTRAINT "evidence_packages_company_id_companies_id_fk" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence_packages" ADD CONSTRAINT "evidence_packages_collection_job_id_issues_id_fk" FOREIGN KEY ("collection_job_id") REFERENCES "public"."issues"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence_packages" ADD CONSTRAINT "evidence_packages_collection_agent_id_agents_id_fk" FOREIGN KEY ("collection_agent_id") REFERENCES "public"."agents"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence_packages" ADD CONSTRAINT "evidence_packages_duplicate_of_id_evidence_packages_id_fk" FOREIGN KEY ("duplicate_of_id") REFERENCES "public"."evidence_packages"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "agents_company_collection_source_type_idx" ON "agents" USING btree ("company_id","collection_source_type");--> statement-breakpoint
CREATE INDEX "issues_company_collection_source_type_idx" ON "issues" USING btree ("company_id","collection_source_type");--> statement-breakpoint
CREATE INDEX "evidence_packages_company_job_idx" ON "evidence_packages" USING btree ("company_id","collection_job_id");--> statement-breakpoint
CREATE INDEX "evidence_packages_company_agent_idx" ON "evidence_packages" USING btree ("company_id","collection_agent_id");--> statement-breakpoint
CREATE INDEX "evidence_packages_company_source_type_idx" ON "evidence_packages" USING btree ("company_id","source_type");--> statement-breakpoint
CREATE INDEX "evidence_packages_company_duplicate_of_idx" ON "evidence_packages" USING btree ("company_id","duplicate_of_id");--> statement-breakpoint
CREATE UNIQUE INDEX "evidence_packages_company_canonical_dedupe_uq" ON "evidence_packages" USING btree ("company_id","dedupe_key") WHERE "evidence_packages"."duplicate_of_id" is null;
