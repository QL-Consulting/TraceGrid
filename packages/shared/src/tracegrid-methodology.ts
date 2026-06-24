export const TRACEGRID_METHODOLOGY_STEP_IDS = [
  "observe_environment",
  "collect_signals",
  "filter_noise",
  "corroborate",
  "map_relationships",
  "assess_confidence",
  "produce_understanding",
] as const;

export type TraceGridMethodologyStepId = (typeof TRACEGRID_METHODOLOGY_STEP_IDS)[number];

export const TRACEGRID_METHODOLOGY_STEP_LABELS: Record<TraceGridMethodologyStepId, string> = {
  observe_environment: "Observe Environment",
  collect_signals: "Collect Signals",
  filter_noise: "Filter Noise",
  corroborate: "Corroborate",
  map_relationships: "Map Relationships",
  assess_confidence: "Assess Confidence",
  produce_understanding: "Produce Understanding",
};

export const TRACEGRID_METHODOLOGY_STEP_WEIGHTS: Record<TraceGridMethodologyStepId, number> = {
  observe_environment: 13.32,
  collect_signals: 19.39,
  filter_noise: 10.77,
  corroborate: 17.37,
  map_relationships: 14.65,
  assess_confidence: 17.89,
  produce_understanding: 6.61,
};

export const TRACEGRID_METHODOLOGY_TOTAL_WEIGHT = 100;
export const TRACEGRID_METHODOLOGY_MAX_STEP_SCORE = 5;
export const TRACEGRID_METHODOLOGY_SCORE_VALUES = [0, 1, 2, 3, 4, 5] as const;

export type TraceGridMethodologyScore = (typeof TRACEGRID_METHODOLOGY_SCORE_VALUES)[number];
export type TraceGridMethodologyScoreMap = Record<TraceGridMethodologyStepId, TraceGridMethodologyScore>;

export const TRACEGRID_CONFIDENCE_BANDS = [
  { id: "very_low", label: "Very Low Confidence", min: 0, max: 0.2 },
  { id: "low", label: "Low Confidence", min: 0.21, max: 0.4 },
  { id: "moderate", label: "Moderate Confidence", min: 0.41, max: 0.6 },
  { id: "high", label: "High Confidence", min: 0.61, max: 0.8 },
  { id: "very_high", label: "Very High Confidence", min: 0.81, max: 1 },
] as const;

export type TraceGridConfidenceBand = (typeof TRACEGRID_CONFIDENCE_BANDS)[number];
export type TraceGridConfidenceBandId = TraceGridConfidenceBand["id"];

export interface TraceGridConfidenceCalculation {
  weightedScore: number;
  maxWeightedScore: number;
  normalizedConfidence: number;
  confidenceBand: TraceGridConfidenceBand;
}

export interface TraceGridCollectionAssessmentOutput {
  claim_assessed: string;
  sources_examined: string[];
  signals_collected: string[];
  noise_removed: string[];
  corroborating_evidence: string[];
  contradictory_evidence: string[];
  relationships_identified: string[];
  confidence_score: number;
  confidence_rationale: string;
  collection_gaps: string[];
  recommended_follow_on_collection: string[];
  assessment_summary: string;
}

function assertTraceGridMethodologyScore(stepId: TraceGridMethodologyStepId, score: number): asserts score is TraceGridMethodologyScore {
  if (!Number.isInteger(score) || score < 0 || score > TRACEGRID_METHODOLOGY_MAX_STEP_SCORE) {
    throw new RangeError(`TraceGrid methodology score for ${stepId} must be an integer from 0 to 5.`);
  }
}

export function getTraceGridConfidenceBand(normalizedConfidence: number): TraceGridConfidenceBand {
  if (!Number.isFinite(normalizedConfidence) || normalizedConfidence < 0 || normalizedConfidence > 1) {
    throw new RangeError("TraceGrid normalized confidence must be a finite number from 0 to 1.");
  }

  if (normalizedConfidence <= 0.2) return TRACEGRID_CONFIDENCE_BANDS[0];
  if (normalizedConfidence <= 0.4) return TRACEGRID_CONFIDENCE_BANDS[1];
  if (normalizedConfidence <= 0.6) return TRACEGRID_CONFIDENCE_BANDS[2];
  if (normalizedConfidence <= 0.8) return TRACEGRID_CONFIDENCE_BANDS[3];
  return TRACEGRID_CONFIDENCE_BANDS[4];
}

export function calculateTraceGridNormalizedConfidence(
  scores: TraceGridMethodologyScoreMap,
): TraceGridConfidenceCalculation {
  let weightedScore = 0;

  for (const stepId of TRACEGRID_METHODOLOGY_STEP_IDS) {
    const score = scores[stepId];
    assertTraceGridMethodologyScore(stepId, score);
    weightedScore += score * TRACEGRID_METHODOLOGY_STEP_WEIGHTS[stepId];
  }

  const maxWeightedScore = TRACEGRID_METHODOLOGY_MAX_STEP_SCORE * TRACEGRID_METHODOLOGY_TOTAL_WEIGHT;
  const normalizedConfidence = weightedScore / maxWeightedScore;

  return {
    weightedScore,
    maxWeightedScore,
    normalizedConfidence,
    confidenceBand: getTraceGridConfidenceBand(normalizedConfidence),
  };
}
