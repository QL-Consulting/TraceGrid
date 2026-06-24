export const TRACEGRID_TERMINOLOGY = {
  product: {
    name: "TraceGrid",
    legacyName: "Paperclip",
  },
  upstreamSystem: {
    name: "Axiom Forge",
    purpose: "Sends collection directives and performs interpretation/synthesis outside TraceGrid.",
  },
  entities: {
    collectionNetwork: {
      label: "Collection Network",
      pluralLabel: "Collection Networks",
      legacyTerms: ["Company", "Team"],
    },
    collectionAgent: {
      label: "Collection Agent",
      pluralLabel: "Collection Agents",
      legacyTerms: ["Agent"],
    },
    tracegridCoordinator: {
      label: "TraceGrid Coordinator",
      pluralLabel: "TraceGrid Coordinators",
      legacyTerms: ["Manager", "CEO"],
    },
    collectionJob: {
      label: "Collection Job",
      pluralLabel: "Collection Jobs",
      legacyTerms: ["Task", "Issue"],
    },
    collectionDirective: {
      label: "Collection Directive",
      pluralLabel: "Collection Directives",
      legacyTerms: ["Goal"],
    },
    evidencePackage: {
      label: "Evidence Package",
      pluralLabel: "Evidence Packages",
      legacyTerms: ["Report", "Artifact", "Work Product"],
    },
    collectionRun: {
      label: "Collection Run",
      pluralLabel: "Collection Runs",
      legacyTerms: ["Heartbeat", "Run"],
    },
  },
  boundaries: {
    noAgentToAgentCommunication: "Collection Agents do not communicate with each other.",
    noFinalAnalysis: "TraceGrid does not produce final analysis, conclusions, judgments, or recommendations.",
    evidenceOnly: "TraceGrid collects, normalizes, deduplicates, retrieves, and packages evidence.",
  },
} as const;

export type TraceGridTerminology = typeof TRACEGRID_TERMINOLOGY;
