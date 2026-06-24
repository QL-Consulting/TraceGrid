import { randomUUID } from "node:crypto";
import express from "express";
import request from "supertest";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  activityLog,
  agents,
  companies,
  createDb,
  evidencePackages,
  issues,
} from "@paperclipai/db";
import {
  getEmbeddedPostgresTestSupport,
  startEmbeddedPostgresTestDatabase,
} from "./helpers/embedded-postgres.js";
import { errorHandler } from "../middleware/index.js";
import { evidencePackageRoutes } from "../routes/evidence-packages.js";

const embeddedPostgresSupport = await getEmbeddedPostgresTestSupport();
const describeEmbeddedPostgres = embeddedPostgresSupport.supported ? describe : describe.skip;

if (!embeddedPostgresSupport.supported) {
  console.warn(
    `Skipping embedded Postgres evidence package route tests on this host: ${embeddedPostgresSupport.reason ?? "unsupported environment"}`,
  );
}

describeEmbeddedPostgres("TraceGrid evidence package routes", () => {
  let db!: ReturnType<typeof createDb>;
  let tempDb: Awaited<ReturnType<typeof startEmbeddedPostgresTestDatabase>> | null = null;
  let companyId!: string;
  let agentId!: string;
  let issueId!: string;
  let actor: Express.Request["actor"];

  beforeAll(async () => {
    tempDb = await startEmbeddedPostgresTestDatabase("tracegrid-evidence-routes-");
    db = createDb(tempDb.connectionString);
  }, 20_000);

  afterEach(async () => {
    await db.delete(evidencePackages);
    await db.delete(activityLog);
    await db.delete(issues);
    await db.delete(agents);
    await db.delete(companies);
  });

  afterAll(async () => {
    await tempDb?.cleanup();
  });

  async function seedNetwork(sourceType = "web") {
    companyId = randomUUID();
    agentId = randomUUID();
    issueId = randomUUID();
    await db.insert(companies).values({
      id: companyId,
      name: "TraceGrid Test Network",
      issuePrefix: `TG${companyId.replace(/-/g, "").slice(0, 5).toUpperCase()}`,
    });
    await db.insert(agents).values({
      id: agentId,
      companyId,
      name: "Web Agent",
      role: "researcher",
      adapterType: "process",
      adapterConfig: {},
      collectionSourceType: sourceType,
    });
    await db.insert(issues).values({
      id: issueId,
      companyId,
      title: "Collect web evidence",
      status: "todo",
      assigneeAgentId: agentId,
      collectionSourceType: sourceType,
    });
    actor = {
      type: "agent",
      agentId,
      companyId,
      source: "agent_key",
    };
  }

  function createApp() {
    const app = express();
    app.use(express.json());
    app.use((req, _res, next) => {
      req.actor = actor;
      next();
    });
    app.use("/api", evidencePackageRoutes(db));
    app.use(errorHandler);
    return app;
  }

  function evidencePayload(overrides: Record<string, unknown> = {}) {
    return {
      source_type: "web",
      source_name: "Example Site",
      url: "https://example.com/evidence#fragment",
      title: "Collected source",
      author: null,
      published_at: null,
      retrieved_at: "2026-06-24T12:00:00.000Z",
      raw_text: "Raw source text from the assigned source.",
      media_urls: [],
      metadata: { retrieval_method: "test" },
      collection_agent: "Web Agent",
      collection_job_id: issueId,
      confidence: 0.9,
      limitations: ["Test fixture; no live retrieval was performed."],
      ...overrides,
    };
  }

  it("lets an assigned collection agent create, list, and fetch an evidence package", async () => {
    await seedNetwork();

    const createResponse = await request(createApp())
      .post(`/api/collection-jobs/${issueId}/evidence-packages`)
      .send(evidencePayload());

    expect(createResponse.status).toBe(201);
    expect(createResponse.body).toMatchObject({
      source_type: "web",
      source_name: "Example Site",
      collection_agent: "Web Agent",
      collection_agent_id: agentId,
      collection_job_id: issueId,
      duplicate_of_id: null,
    });
    expect(createResponse.body.id).toEqual(expect.any(String));
    expect(createResponse.body.content_hash).toEqual(expect.any(String));

    actor = {
      type: "board",
      source: "local_implicit",
      userId: "local-board",
      isInstanceAdmin: true,
    };
    const listResponse = await request(createApp())
      .get(`/api/collection-jobs/${issueId}/evidence-packages`);
    expect(listResponse.status).toBe(200);
    expect(listResponse.body).toHaveLength(1);
    expect(listResponse.body[0].id).toBe(createResponse.body.id);

    const getResponse = await request(createApp())
      .get(`/api/evidence-packages/${createResponse.body.id}`);
    expect(getResponse.status).toBe(200);
    expect(getResponse.body.id).toBe(createResponse.body.id);
  });

  it("marks repeated source evidence as a duplicate of the canonical package", async () => {
    await seedNetwork();

    const app = createApp();
    const first = await request(app)
      .post(`/api/collection-jobs/${issueId}/evidence-packages`)
      .send(evidencePayload());
    const second = await request(app)
      .post(`/api/collection-jobs/${issueId}/evidence-packages`)
      .send(evidencePayload({
        url: "https://EXAMPLE.com:443/evidence#other-fragment",
      }));

    expect(first.status).toBe(201);
    expect(second.status).toBe(201);
    expect(second.body.duplicate_of_id).toBe(first.body.id);
  });

  it("rejects source-type mismatches for the authenticated collection agent", async () => {
    await seedNetwork("news_rss");

    const response = await request(createApp())
      .post(`/api/collection-jobs/${issueId}/evidence-packages`)
      .send(evidencePayload({
        source_type: "web",
      }));

    expect(response.status).toBe(422);
    expect(response.body.error).toContain("collection job source type");
  });

  it("requires collection agent auth for evidence creation", async () => {
    await seedNetwork();
    actor = {
      type: "board",
      source: "local_implicit",
      userId: "local-board",
      isInstanceAdmin: true,
    };

    const response = await request(createApp())
      .post(`/api/collection-jobs/${issueId}/evidence-packages`)
      .send(evidencePayload());

    expect(response.status).toBe(403);
    expect(response.body.error).toBe("Collection agent authentication required to create evidence packages");
  });
});
