import { randomUUID } from "node:crypto";
import express from "express";
import request from "supertest";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  agents,
  companies,
  createDb,
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

  beforeAll(async () => {
    tempDb = await startEmbeddedPostgresTestDatabase("tracegrid-alias-routes-");
    db = createDb(tempDb.connectionString);
  }, 20_000);

  afterEach(async () => {
    await db.delete(issues);
    await db.delete(goals);
    await db.delete(agents);
    await db.delete(companies);
  });

  afterAll(async () => {
    await tempDb?.cleanup();
  });

  function createApp() {
    const app = express();
    app.use(express.json());
    app.use((req, _res, next) => {
      req.actor = {
        type: "board",
        source: "local_implicit",
        userId: "local-board",
        isInstanceAdmin: true,
      };
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
  });
});
