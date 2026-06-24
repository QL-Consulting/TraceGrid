import { describe, expect, it } from "vitest";
import {
  calculateTraceGridNormalizedConfidence,
  getTraceGridConfidenceBand,
  TRACEGRID_METHODOLOGY_STEP_WEIGHTS,
  type TraceGridMethodologyScoreMap,
} from "./tracegrid-methodology.js";

const allScores = (score: TraceGridMethodologyScoreMap[keyof TraceGridMethodologyScoreMap]): TraceGridMethodologyScoreMap => ({
  observe_environment: score,
  collect_signals: score,
  filter_noise: score,
  corroborate: score,
  map_relationships: score,
  assess_confidence: score,
  produce_understanding: score,
});

describe("TraceGrid methodology confidence scoring", () => {
  it("normalizes weighted methodology scores against a 500 point maximum", () => {
    const result = calculateTraceGridNormalizedConfidence({
      observe_environment: 4,
      collect_signals: 5,
      filter_noise: 3,
      corroborate: 4,
      map_relationships: 3,
      assess_confidence: 4,
      produce_understanding: 2,
    });

    const expectedWeightedScore =
      (4 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.observe_environment) +
      (5 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.collect_signals) +
      (3 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.filter_noise) +
      (4 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.corroborate) +
      (3 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.map_relationships) +
      (4 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.assess_confidence) +
      (2 * TRACEGRID_METHODOLOGY_STEP_WEIGHTS.produce_understanding);

    expect(result.weightedScore).toBeCloseTo(expectedWeightedScore);
    expect(result.maxWeightedScore).toBe(500);
    expect(result.normalizedConfidence).toBeCloseTo(expectedWeightedScore / 500);
    expect(result.confidenceBand.label).toBe("High Confidence");
  });

  it("returns very low and very high bands at the score extremes", () => {
    expect(calculateTraceGridNormalizedConfidence(allScores(0)).confidenceBand.label).toBe("Very Low Confidence");
    expect(calculateTraceGridNormalizedConfidence(allScores(5)).confidenceBand.label).toBe("Very High Confidence");
  });

  it("maps normalized confidence thresholds to canonical bands", () => {
    expect(getTraceGridConfidenceBand(0.2).label).toBe("Very Low Confidence");
    expect(getTraceGridConfidenceBand(0.21).label).toBe("Low Confidence");
    expect(getTraceGridConfidenceBand(0.41).label).toBe("Moderate Confidence");
    expect(getTraceGridConfidenceBand(0.61).label).toBe("High Confidence");
    expect(getTraceGridConfidenceBand(0.81).label).toBe("Very High Confidence");
  });

  it("rejects scores outside the required 0 to 5 scale", () => {
    expect(() =>
      calculateTraceGridNormalizedConfidence({
        ...allScores(3),
        assess_confidence: 6,
      } as unknown as TraceGridMethodologyScoreMap),
    ).toThrow(RangeError);
  });
});
