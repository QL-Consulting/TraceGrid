import { Router } from "express";
import type { Db } from "@paperclipai/db";
import {
  agentService,
  companyService,
  goalService,
  issueService,
} from "../services/index.js";
import { assertBoard, assertCompanyAccess } from "./authz.js";
import { notFound } from "../errors.js";

export function traceGridAliasRoutes(db: Db) {
  const router = Router();
  const companies = companyService(db);
  const agents = agentService(db);
  const issues = issueService(db);
  const goals = goalService(db);

  router.get("/collection-networks", async (req, res) => {
    assertBoard(req);
    const rows = await companies.list();
    if (req.actor.source === "local_implicit" || req.actor.isInstanceAdmin) {
      res.json(rows);
      return;
    }
    const allowed = new Set(req.actor.companyIds ?? []);
    res.json(rows.filter((company) => allowed.has(company.id)));
  });

  router.get("/collection-networks/:networkId", async (req, res) => {
    const networkId = req.params.networkId as string;
    assertCompanyAccess(req, networkId);
    assertBoard(req);
    const network = await companies.getById(networkId);
    if (!network) throw notFound("Collection network not found");
    res.json(network);
  });

  router.get("/collection-networks/:networkId/collection-agents", async (req, res) => {
    const networkId = req.params.networkId as string;
    assertCompanyAccess(req, networkId);
    assertBoard(req);
    res.json(await agents.list(networkId));
  });

  router.get("/collection-agents/:agentId", async (req, res) => {
    assertBoard(req);
    const agent = await agents.getById(req.params.agentId as string);
    if (!agent) throw notFound("Collection agent not found");
    assertCompanyAccess(req, agent.companyId);
    res.json(agent);
  });

  router.get("/collection-networks/:networkId/collection-jobs", async (req, res) => {
    const networkId = req.params.networkId as string;
    assertCompanyAccess(req, networkId);
    assertBoard(req);
    res.json(await issues.list(networkId));
  });

  router.get("/collection-jobs/:jobId", async (req, res) => {
    assertBoard(req);
    const job = await issues.getById(req.params.jobId as string);
    if (!job) throw notFound("Collection job not found");
    assertCompanyAccess(req, job.companyId);
    res.json(job);
  });

  router.get("/collection-networks/:networkId/collection-directives", async (req, res) => {
    const networkId = req.params.networkId as string;
    assertCompanyAccess(req, networkId);
    assertBoard(req);
    res.json(await goals.list(networkId));
  });

  router.get("/collection-directives/:directiveId", async (req, res) => {
    assertBoard(req);
    const directive = await goals.getById(req.params.directiveId as string);
    if (!directive) throw notFound("Collection directive not found");
    assertCompanyAccess(req, directive.companyId);
    res.json(directive);
  });

  return router;
}
