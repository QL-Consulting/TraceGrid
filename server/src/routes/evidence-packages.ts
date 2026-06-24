import { Router } from "express";
import type { Db } from "@paperclipai/db";
import { agents, issues } from "@paperclipai/db";
import { and, eq } from "drizzle-orm";
import { evidencePackageSchema } from "@paperclipai/shared";
import { validate } from "../middleware/validate.js";
import { forbidden, notFound } from "../errors.js";
import { evidencePackageService, logActivity } from "../services/index.js";
import { assertCompanyAccess, getActorInfo } from "./authz.js";

async function loadCollectionJob(db: Db, collectionJobId: string) {
  return db
    .select({
      id: issues.id,
      companyId: issues.companyId,
      assigneeAgentId: issues.assigneeAgentId,
    })
    .from(issues)
    .where(eq(issues.id, collectionJobId))
    .then((rows) => rows[0] ?? null);
}

async function loadEvidenceAccessCompanyId(
  svc: ReturnType<typeof evidencePackageService>,
  evidencePackageId: string,
) {
  const evidencePackage = await svc.getById(evidencePackageId);
  return evidencePackage?.company_id ?? null;
}

async function assertCollectionAgentCanCreateEvidence(input: {
  db: Db;
  actor: Express.Request["actor"];
  collectionJob: { id: string; companyId: string; assigneeAgentId: string | null };
}) {
  if (input.actor.type !== "agent" || !input.actor.agentId) {
    throw forbidden("Collection agent authentication required to create evidence packages");
  }
  if (input.actor.companyId !== input.collectionJob.companyId) {
    throw forbidden("Collection agent cannot create evidence outside its collection network");
  }
  if (
    input.collectionJob.assigneeAgentId &&
    input.collectionJob.assigneeAgentId !== input.actor.agentId
  ) {
    throw forbidden("Collection agent cannot create evidence for another agent's collection job");
  }

  const agent = await input.db
    .select({ id: agents.id })
    .from(agents)
    .where(and(
      eq(agents.id, input.actor.agentId),
      eq(agents.companyId, input.collectionJob.companyId),
    ))
    .then((rows) => rows[0] ?? null);
  if (!agent) {
    throw forbidden("Collection agent is not part of this collection network");
  }
}

export function evidencePackageRoutes(db: Db) {
  const router = Router();
  const svc = evidencePackageService(db);

  router.get("/collection-jobs/:collectionJobId/evidence-packages", async (req, res) => {
    const collectionJobId = req.params.collectionJobId as string;
    const collectionJob = await loadCollectionJob(db, collectionJobId);
    if (!collectionJob) throw notFound("Collection job not found");
    assertCompanyAccess(req, collectionJob.companyId);
    res.json(await svc.listForCollectionJob(collectionJob.companyId, collectionJob.id));
  });

  router.post(
    "/collection-jobs/:collectionJobId/evidence-packages",
    validate(evidencePackageSchema),
    async (req, res) => {
      const collectionJobId = req.params.collectionJobId as string;
      const collectionJob = await loadCollectionJob(db, collectionJobId);
      if (!collectionJob) throw notFound("Collection job not found");
      assertCompanyAccess(req, collectionJob.companyId);
      await assertCollectionAgentCanCreateEvidence({
        db,
        actor: req.actor,
        collectionJob,
      });

      const actor = getActorInfo(req);
      const evidencePackage = await svc.createForCollectionJob({
        companyId: collectionJob.companyId,
        collectionJobId: collectionJob.id,
        collectionAgentId: req.actor.type === "agent" ? req.actor.agentId! : "",
        evidence: req.body,
      });
      await logActivity(db, {
        companyId: collectionJob.companyId,
        actorType: actor.actorType,
        actorId: actor.actorId,
        agentId: actor.agentId,
        runId: actor.runId,
        action: evidencePackage.duplicate_of_id
          ? "evidence_package.deduplicated"
          : "evidence_package.created",
        entityType: "evidence_package",
        entityId: evidencePackage.id,
        details: {
          collectionJobId: collectionJob.id,
          sourceType: evidencePackage.source_type,
          duplicateOfId: evidencePackage.duplicate_of_id,
        },
      });
      res.status(201).json(evidencePackage);
    },
  );

  router.get("/evidence-packages/:evidencePackageId", async (req, res) => {
    const evidencePackageId = req.params.evidencePackageId as string;
    const companyId = await loadEvidenceAccessCompanyId(svc, evidencePackageId);
    if (!companyId) throw notFound("Evidence package not found");
    assertCompanyAccess(req, companyId);
    const evidencePackage = await svc.getById(evidencePackageId);
    res.json(evidencePackage);
  });

  return router;
}
