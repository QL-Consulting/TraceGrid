import { randomUUID } from "node:crypto";
import express from "express";
import type { Request } from "express";
import request from "supertest";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  activityLog,
  agents,
  companies,
  createDb,
  evidencePackages,
  goals,
  issues,
} from "@paperclipai/db";
import {
  getEmbeddedPostgresTestSupport,
  startEmbeddedPostgresTestDatabase,
} from "./helpers/embedded-postgres.js";
import { errorHandler } from "../middleware/index.js";
import { traceGridAliasRoutes } from "../routes/tracegrid-aliases.js";

const embeddedPostgresSupport = await getEmbeddedPostgresTestSupport();
const describeEmbeddedPostgres = embeddedPostgresSupport.supported ? describe : describe.skip;

if (!embeddedPostgresSupport.supported) {
  console.warn(
    `Skipping embedded Postgres TraceGrid alias route tests on this host: ${embeddedPostgresSupport.reason ?? "unsupported environment"}`,
  );
}

describeEmbeddedPostgres("TraceGrid alias routes", () => {
  let db!: ReturnType<typeof createDb>;
  let tempDb: Awaited<ReturnType<typeof startEmbeddedPostgresTestDatabase>> | null = null;
  const originalTraceGridAxiomToken = process.env.TRACEGRID_AXIOM_TOKEN;

  beforeAll(async () => {
    tempDb = await startEmbeddedPostgresTestDatabase("tracegrid-alias-routes-");
    db = createDb(tempDb.connectionString);
  }, 20_000);

  afterEach(async () => {
    if (originalTraceGridAxiomToken === undefined) {
      delete process.env.TRACEGRID_AXIOM_TOKEN;
    } else {
      process.env.TRACEGRID_AXIOM_TOKEN = originalTraceGridAxiomToken;
    }
    await db.delete(evidencePackages);
    await db.delete(activityLog);
    await db.delete(issues);
    await db.delete(goals);
    await db.delete(agents);
    await db.delete(companies);
  });

  afterAll(async () => {
    await tempDb?.cleanup();
  });

  function createApp(actor: Request["actor"] = {
    type: "board",
    source: "local_implicit",
    userId: "local-board",
    isInstanceAdmin: true,
  }) {
    const app = express();
    app.use(express.json());
    app.use((req, _res, next) => {
      req.actor = actor;
      next();
    });
    app.use("/api", traceGridAliasRoutes(db));
    app.use(errorHandler);
    return app;
  }

  it("exposes board-only TraceGrid aliases for networks, agents, jobs, and directives", async () => {
    const companyId = randomUUID();
    const agentId = randomUUID();
    const issueId = randomUUID();
    const goalId = randomUUID();

    await db.insert(companies).values({
      id: companyId,
      name: "TraceGrid Network",
      issuePrefix: `TG${companyId.replace(/-/g, "").slice(0, 5).toUpperCase()}`,
    });
    await db.insert(agents).values({
      id: agentId,
      companyId,
      name: "Web Agent",
      role: "researcher",
      adapterType: "process",
      adapterConfig: {},
      collectionSourceType: "web",
    });
    await db.insert(goals).values({
      id: goalId,
      companyId,
      title: "Collect directive evidence",
      level: "company",
      status: "active",
    });
    await db.insert(issues).values({
      id: issueId,
      companyId,
      title: "Collect web evidence",
      status: "todo",
      assigneeAgentId: agentId,
      goalId,
      collectionSourceType: "web",
    });

    const app = createApp();
    const networks = await request(app).get("/api/collection-networks");
    const network = await request(app).get(`/api/collection-networks/${companyId}`);
    const collectionAgents = await request(app).get(`/api/collection-networks/${companyId}/collection-agents`);
    const collectionJobs = await request(app).get(`/api/collection-networks/${companyId}/collection-jobs`);
    const directives = await request(app).get(`/api/collection-networks/${companyId}/collection-directives`);
    const createdDirective = await request(app)
      .post(`/api/collection-networks/${companyId}/collection-directives`)
      .send({
        title: "Axiom directive",
        description: "Collect source evidence for Axiom Forge.",
        level: "company",
        status: "active",
      });

    expect(networks.status).toBe(200);
    expect(networks.body[0]).toMatchObject({ id: companyId, name: "TraceGrid Network" });
    expect(network.status).toBe(200);
    expect(network.body.id).toBe(companyId);
    expect(collectionAgents.status).toBe(200);
    expect(collectionAgents.body[0]).toMatchObject({
      id: agentId,
      collectionSourceType: "web",
    });
    expect(collectionJobs.status).toBe(200);
    expect(collectionJobs.body[0]).toMatchObject({
      id: issueId,
      collectionSourceType: "web",
    });
    expect(directives.status).toBe(200);
    expect(directives.body[0]).toMatchObject({ id: goalId });
    expect(createdDirective.status).toBe(201);
    expect(createdDirective.body).toMatchObject({
      companyId,
      title: "Axiom directive",
    });
  });

  it("retrieves evidence packages by collection directive", async () => {
    const companyId = randomUUID();
    const agentId = randomUUID();
    const issueId = randomUUID();
    const goalId = randomUUID();
    const evidenceId = randomUUID();

    await db.insert(companies).values({
      id: companyId,
      name: "TraceGrid Evidence Network",
      issuePrefix: `TE${companyId.replace(/-/g, "").slice(0, 5).toUpperCase()}`,
    });
    await db.insert(agents).values({
      id: agentId,
      companyId,
      name: "Document Agent",
      role: "researcher",
      adapterType: "process",
      adapterConfig: {},
      collectionSourceType: "document_pdf",
    });
    await db.insert(goals).values({
      id: goalId,
      companyId,
      title: "Collect documents",
      level: "company",
      status: "active",
    });
    await db.insert(issues).values({
      id: issueId,
      companyId,
      title: "Collect PDF evidence",
      status: "todo",
      assigneeAgentId: agentId,
      goalId,
      collectionSourceType: "document_pdf",
    });
    await db.insert(evidencePackages).values({
      id: evidenceId,
      companyId,
      collectionJobId: issueId,
      collectionAgentId: agentId,
      sourceType: "document_pdf",
      sourceName: "Example PDF",
      url: "https://example.com/doc.pdf",
      title: "Example PDF",
      author: null,
      retrievedAt: new Date("2026-06-24T12:00:00.000Z"),
      rawText: "Raw PDF text",
      mediaUrls: [],
      metadata: {},
      collectionAgent: "Document Agent",
      confidence: 0.8,
      limitations: ["Test fixture"],
      contentHash: "hash",
      dedupeKey: "dedupe",
    });

    const response = await request(createApp())
      .get(`/api/collection-directives/${goalId}/evidence-packages`);

    expect(response.status).toBe(200);
    expect(response.body).toHaveLength(1);
    expect(response.body[0]).toMatchObject({
      id: evidenceId,
      collection_job_id: issueId,
      source_type: "document_pdf",
    });
  });

  it("allows Axiom Forge token access to create directives and retrieve directive evidence", async () => {
    process.env.TRACEGRID_AXIOM_TOKEN = "axiom-secret";
    const companyId = randomUUID();
    const agentId = randomUUID();
    const issueId = randomUUID();

    await db.insert(companies).values({
      id: companyId,
      name: "Axiom Linked Network",
      issuePrefix: `AX${companyId.replace(/-/g, "").slice(0, 5).toUpperCase()}`,
    });
    await db.insert(agents).values({
      id: agentId,
      companyId,
      name: "Web Agent",
      role: "researcher",
      adapterType: "process",
      adapterConfig: {},
      collectionSourceType: "web",
    });

    const app = createApp({ type: "none", source: "none" });
    const createdDirective = await request(app)
      .post(`/api/collection-networks/${companyId}/collection-directives`)
      .set("x-tracegrid-axiom-token", "axiom-secret")
      .send({
        title: "Axiom collection directive",
        description: "Collect evidence requested by Axiom Forge.",
        level: "company",
        status: "active",
      });

    expect(createdDirective.status).toBe(201);
    expect(createdDirective.body).toMatchObject({
      companyId,
      title: "Axiom collection directive",
    });

    await db.insert(issues).values({
      id: issueId,
      companyId,
      title: "Collect web evidence",
      status: "todo",
      assigneeAgentId: agentId,
      goalId: createdDirective.body.id,
      collectionSourceType: "web",
    });
    await db.insert(evidencePackages).values({
      companyId,
      collectionJobId: issueId,
      collectionAgentId: agentId,
      sourceType: "web",
      sourceName: "Example Site",
      url: "https://example.com",
      title: "Example Site",
      retrievedAt: new Date("2026-06-24T12:00:00.000Z"),
      rawText: "Raw web evidence",
      mediaUrls: [],
      metadata: {},
      collectionAgent: "Web Agent",
      confidence: 0.75,
      limitations: ["Test fixture"],
      contentHash: "hash-axiom",
      dedupeKey: "dedupe-axiom",
    });

    const evidence = await request(app)
      .get(`/api/collection-directives/${createdDirective.body.id}/evidence-packages`)
      .set("authorization", "Bearer axiom-secret");

    expect(evidence.status).toBe(200);
    expect(evidence.body).toHaveLength(1);
    expect(evidence.body[0]).toMatchObject({
      source_type: "web",
      collection_job_id: issueId,
    });
  });

  it("rejects Axiom-facing directive access without the configured token", async () => {
    process.env.TRACEGRID_AXIOM_TOKEN = "axiom-secret";
    const companyId = randomUUID();
    await db.insert(companies).values({
      id: companyId,
      name: "Axiom Protected Network",
      issuePrefix: `AP${companyId.replace(/-/g, "").slice(0, 5).toUpperCase()}`,
    });

    const app = createApp({ type: "none", source: "none" });
    const response = await request(app)
      .post(`/api/collection-networks/${companyId}/collection-directives`)
      .set("x-tracegrid-axiom-token", "wrong-token")
      .send({
        title: "Unauthorized directive",
        level: "company",
        status: "planned",
      });

    expect(response.status).toBe(401);
  });
});
