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
    collectionCell: {
      label: "Collection Cell",
      pluralLabel: "Collection Cells",
      legacyTerms: ["Company", "Team"],
      acceptedSynonyms: ["Intelligence Cell", "Mission Cell"],
    },
    collectionNetwork: {
      label: "Collection Network",
      pluralLabel: "Collection Networks",
      legacyTerms: ["Company", "Team"],
      note: "Compatibility and higher-level grouping term for distributed or multi-cell structures.",
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
    noFinalAnalysis: "TraceGrid does not produce final analysis, final truth determinations, conclusions, judgments, or recommendations.",
    evidenceOnly: "TraceGrid collects, structures, scores, normalizes, deduplicates, retrieves, and packages evidence.",
    methodology: "TraceGrid transforms uncertainty into defensible confidence through a structured epistemological workflow.",
  },
} as const;

export type TraceGridTerminology = typeof TRACEGRID_TERMINOLOGY;
