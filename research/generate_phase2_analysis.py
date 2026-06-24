#!/usr/bin/env python3
"""Generate Phase II TraceGrid weighting analyses from the Phase I corpus.

This script intentionally does not regenerate `case_studies.csv` or
`case_studies.json`. It reads the existing corpus and derives secondary
architecture-oriented analyses: impact, frequency, recoverability, modality
weights, fusion trust, and the final TraceGrid weighting model.
"""

from __future__ import annotations

import csv
import datetime as dt
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CASE_CSV = ROOT / "case_studies.csv"

STEPS = [
    ("observe", "Observe Digital Environment"),
    ("collect_signals", "Collect Signals"),
    ("filter_noise", "Filter Noise"),
    ("corroborate", "Corroborate"),
    ("map_relationships", "Map Relationships"),
    ("assess_confidence", "Assess Confidence"),
    ("produce_understanding", "Produce Understanding"),
]

PROFESSIONS = [
    "OSINT Intelligence Analyst",
    "OSINT Investigative Journalist",
    "Cyber Threat Intelligence Analyst",
    "Meteorologist / Weather Forecaster",
    "Quantitative Trader / Market Analyst",
    "Competitive Intelligence Analyst",
]

DEGRADATION = {
    0: "No Impact",
    1: "Minor Impact",
    2: "Moderate Impact",
    3: "Severe Impact",
    4: "Catastrophic Impact",
}

# Workflow-structure prior: if a stage completely fails, how hard is it for
# later stages to repair? These values are not copied from Phase I; they encode
# the logic of a sequential evidence workflow and are blended with observed
# Phase I failure propagation below.
STRUCTURAL_RECOVERABILITY_PRIOR = {
    "observe": 2.4,
    "collect_signals": 4.0,
    "filter_noise": 2.6,
    "corroborate": 3.2,
    "map_relationships": 2.2,
    "assess_confidence": 3.5,
    "produce_understanding": 1.0,
}

RECOVERY_LABELS = {
    0: "Fully Recoverable",
    1: "Mostly Recoverable",
    2: "Partially Recoverable",
    3: "Rarely Recoverable",
    4: "Not Recoverable",
}

MODALITIES = [
    "Web Search Agent",
    "News Agent",
    "Social Media Agent",
    "Public Records Agent",
    "Academic / Research Agent",
    "Video / Media Agent",
    "Forum Agent",
    "Geospatial / Imagery Agent",
]

MISSION_CONDITIONS = [
    "General Intelligence",
    "Influence Operations",
    "Information Warfare",
    "Competitive Intelligence",
    "National Security Monitoring",
    "Crisis Monitoring",
    "Strategic Warning",
]


def load_rows() -> list[dict[str, str]]:
    with CASE_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def score(row: dict[str, str], step: str) -> int:
    return int(row.get(f"{step}_impact_score", 0) or 0)


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def normalize(values: dict[str, float], digits: int = 2) -> dict[str, float]:
    total = sum(max(0.0, value) for value in values.values()) or 1.0
    normalized = {key: round(max(0.0, value) / total * 100, digits) for key, value in values.items()}
    diff = round(100.0 - sum(normalized.values()), digits)
    if normalized and diff:
        key = max(normalized, key=normalized.get)
        normalized[key] = round(normalized[key] + diff, digits)
    return normalized


def metric_bundle(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    metrics: dict[str, dict[str, float]] = {}
    n = len(rows) or 1
    for step, _label in STEPS:
        values = [score(row, step) for row in rows]
        failing = [value for value in values if value > 0]
        metrics[step] = {
            "average": round(statistics.mean(values), 4) if values else 0.0,
            "median": round(statistics.median(values), 4) if values else 0.0,
            "stdev": round(statistics.pstdev(values), 4) if len(values) > 1 else 0.0,
            "failure_frequency": round(sum(1 for value in values if value > 0) / n, 4),
            "major_failure_frequency": round(sum(1 for value in values if value >= 3) / n, 4),
            "catastrophic_frequency": round(sum(1 for value in values if value == 4) / n, 4),
            "failure_count": sum(1 for value in values if value > 0),
            "major_failure_count": sum(1 for value in values if value >= 3),
            "catastrophic_count": sum(1 for value in values if value == 4),
            "avg_when_failed": round(statistics.mean(failing), 4) if failing else 0.0,
        }
    return metrics


def grouped_metrics(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, dict[str, float]]]]:
    global_metrics = metric_bundle(rows)
    by_profession: dict[str, dict[str, dict[str, float]]] = {}
    for profession in PROFESSIONS:
        subset = [row for row in rows if row["profession"] == profession]
        by_profession[profession] = metric_bundle(subset)
    return global_metrics, by_profession


def ranking(metrics: dict[str, dict[str, float]], key: str = "average") -> list[tuple[str, float]]:
    return sorted(
        ((label, metrics[step][key]) for step, label in STEPS),
        key=lambda item: item[1],
        reverse=True,
    )


def step_weight_from_metrics(metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    raw = {
        step: (
            metrics[step]["average"] * 0.55
            + metrics[step]["median"] * 0.25
            + metrics[step]["failure_frequency"] * 1.25
            + metrics[step]["catastrophic_frequency"] * 1.75
        )
        for step, _label in STEPS
    }
    return normalize(raw)


def severity_label(value: float) -> str:
    if value < 0.5:
        return RECOVERY_LABELS[0]
    if value < 1.5:
        return RECOVERY_LABELS[1]
    if value < 2.5:
        return RECOVERY_LABELS[2]
    if value < 3.5:
        return RECOVERY_LABELS[3]
    return RECOVERY_LABELS[4]


def downstream_steps(step: str) -> list[str]:
    slugs = [slug for slug, _ in STEPS]
    index = slugs.index(step)
    return slugs[index + 1 :]


def recoverability_scores(rows: list[dict[str, str]], profession: str | None = None) -> dict[str, dict[str, float | str]]:
    subset = rows if profession is None else [row for row in rows if row["profession"] == profession]
    metrics = metric_bundle(subset)
    result: dict[str, dict[str, float | str]] = {}
    for step, _label in STEPS:
        failures = [row for row in subset if score(row, step) > 0]
        if failures:
            major_given_failure = sum(1 for row in failures if score(row, step) >= 3) / len(failures)
            catastrophic_given_failure = sum(1 for row in failures if score(row, step) == 4) / len(failures)
            downstream = downstream_steps(step)
            if downstream:
                downstream_burden = statistics.mean(
                    max(score(row, downstream_step) for downstream_step in downstream) for row in failures
                ) / 4.0
                downstream_clean_rate = sum(
                    1 for row in failures if all(score(row, downstream_step) == 0 for downstream_step in downstream)
                ) / len(failures)
            else:
                downstream_burden = 0.0
                downstream_clean_rate = 1.0
            observed_non_recovery = min(
                4.0,
                metrics[step]["avg_when_failed"] * 0.45
                + major_given_failure * 1.35
                + catastrophic_given_failure * 2.2
                + downstream_burden * 1.0
                - downstream_clean_rate * 0.4,
            )
        else:
            major_given_failure = 0.0
            catastrophic_given_failure = 0.0
            downstream_burden = 0.0
            downstream_clean_rate = 1.0
            observed_non_recovery = 0.0

        prior = STRUCTURAL_RECOVERABILITY_PRIOR[step]
        # Complete failure counterfactual: the prior carries the main causal
        # load, while corpus evidence tempers it where actual failures appear
        # less damaging or more recoverable.
        blended = max(0.0, min(4.0, prior * 0.62 + observed_non_recovery * 0.38))
        result[step] = {
            "recoverability_score": round(blended, 3),
            "recoverability_label": severity_label(blended),
            "structural_prior": round(prior, 2),
            "observed_non_recovery": round(observed_non_recovery, 3),
            "major_given_failure": round(major_given_failure, 4),
            "catastrophic_given_failure": round(catastrophic_given_failure, 4),
            "downstream_clean_rate": round(downstream_clean_rate, 4),
            "downstream_burden": round(downstream_burden, 4),
        }
    return result


def modality_weights(
    global_weights: dict[str, float],
    profession_weights: dict[str, dict[str, float]],
    recovery_global: dict[str, dict[str, float | str]],
) -> dict[str, dict[str, float]]:
    # Medium priors emphasize the workflow stages that become intrinsically
    # important in each collection environment. Values are relative, not final
    # percentages, and are blended with observed profession-derived weights.
    priors: dict[str, dict[str, float]] = {
        "Web Search Agent": {
            "observe": 11,
            "collect_signals": 18,
            "filter_noise": 17,
            "corroborate": 18,
            "map_relationships": 12,
            "assess_confidence": 18,
            "produce_understanding": 6,
        },
        "News Agent": {
            "observe": 14,
            "collect_signals": 19,
            "filter_noise": 14,
            "corroborate": 20,
            "map_relationships": 11,
            "assess_confidence": 16,
            "produce_understanding": 6,
        },
        "Social Media Agent": {
            "observe": 8,
            "collect_signals": 14,
            "filter_noise": 32,
            "corroborate": 20,
            "map_relationships": 10,
            "assess_confidence": 12,
            "produce_understanding": 4,
        },
        "Public Records Agent": {
            "observe": 18,
            "collect_signals": 16,
            "filter_noise": 8,
            "corroborate": 14,
            "map_relationships": 21,
            "assess_confidence": 13,
            "produce_understanding": 10,
        },
        "Academic / Research Agent": {
            "observe": 10,
            "collect_signals": 16,
            "filter_noise": 10,
            "corroborate": 24,
            "map_relationships": 12,
            "assess_confidence": 21,
            "produce_understanding": 7,
        },
        "Video / Media Agent": {
            "observe": 12,
            "collect_signals": 16,
            "filter_noise": 18,
            "corroborate": 22,
            "map_relationships": 17,
            "assess_confidence": 11,
            "produce_understanding": 4,
        },
        "Forum Agent": {
            "observe": 9,
            "collect_signals": 16,
            "filter_noise": 32,
            "corroborate": 17,
            "map_relationships": 12,
            "assess_confidence": 10,
            "produce_understanding": 4,
        },
        "Geospatial / Imagery Agent": {
            "observe": 18,
            "collect_signals": 17,
            "filter_noise": 8,
            "corroborate": 20,
            "map_relationships": 23,
            "assess_confidence": 11,
            "produce_understanding": 3,
        },
    }

    evidence_mix: dict[str, dict[str, float]] = {
        "Web Search Agent": combine_weights(
            [
                (profession_weights["OSINT Intelligence Analyst"], 0.35),
                (profession_weights["OSINT Investigative Journalist"], 0.25),
                (profession_weights["Competitive Intelligence Analyst"], 0.2),
                (global_weights, 0.2),
            ]
        ),
        "News Agent": combine_weights(
            [
                (profession_weights["OSINT Intelligence Analyst"], 0.45),
                (profession_weights["OSINT Investigative Journalist"], 0.35),
                (global_weights, 0.2),
            ]
        ),
        "Social Media Agent": combine_weights(
            [
                (profession_weights["OSINT Investigative Journalist"], 0.25),
                (profession_weights["OSINT Intelligence Analyst"], 0.25),
                (profession_weights["Quantitative Trader / Market Analyst"], 0.2),
                (global_weights, 0.3),
            ]
        ),
        "Public Records Agent": combine_weights(
            [
                (profession_weights["Competitive Intelligence Analyst"], 0.65),
                (profession_weights["Cyber Threat Intelligence Analyst"], 0.15),
                (global_weights, 0.2),
            ]
        ),
        "Academic / Research Agent": combine_weights(
            [
                (profession_weights["OSINT Investigative Journalist"], 0.3),
                (profession_weights["Competitive Intelligence Analyst"], 0.2),
                (global_weights, 0.5),
            ]
        ),
        "Video / Media Agent": combine_weights(
            [
                (profession_weights["OSINT Investigative Journalist"], 0.45),
                (profession_weights["OSINT Intelligence Analyst"], 0.25),
                (global_weights, 0.3),
            ]
        ),
        "Forum Agent": combine_weights(
            [
                (profession_weights["Cyber Threat Intelligence Analyst"], 0.35),
                (profession_weights["OSINT Intelligence Analyst"], 0.25),
                (profession_weights["Quantitative Trader / Market Analyst"], 0.15),
                (global_weights, 0.25),
            ]
        ),
        "Geospatial / Imagery Agent": combine_weights(
            [
                (profession_weights["Meteorologist / Weather Forecaster"], 0.45),
                (profession_weights["OSINT Investigative Journalist"], 0.25),
                (profession_weights["OSINT Intelligence Analyst"], 0.1),
                (global_weights, 0.2),
            ]
        ),
    }

    recovery_weight = normalize({step: float(recovery_global[step]["recoverability_score"]) for step, _ in STEPS})
    final: dict[str, dict[str, float]] = {}
    for modality in MODALITIES:
        raw = {
            step: evidence_mix[modality][step] * 0.45
            + priors[modality][step] * 0.40
            + recovery_weight[step] * 0.15
            for step, _label in STEPS
        }
        final[modality] = normalize(raw)
    return final


def combine_weights(items: list[tuple[dict[str, float], float]]) -> dict[str, float]:
    raw = defaultdict(float)
    for weights, factor in items:
        for step, _label in STEPS:
            raw[step] += weights[step] * factor
    return normalize(dict(raw))


def modality_attributes() -> dict[str, dict[str, float]]:
    # Relative capability profile for fusion. 1.0 means the modality is highly
    # useful for that attribute; 0.0 means weak fit. "noise_resistance" is trust
    # after normal TraceGrid filtering, not raw source cleanliness.
    return {
        "Web Search Agent": {
            "breadth": 0.95,
            "timeliness": 0.72,
            "provenance": 0.55,
            "influence_surface": 0.45,
            "adversarial_surface": 0.55,
            "relationship_value": 0.55,
            "ground_truth": 0.45,
            "strategic_depth": 0.55,
            "noise_resistance": 0.55,
        },
        "News Agent": {
            "breadth": 0.78,
            "timeliness": 0.86,
            "provenance": 0.62,
            "influence_surface": 0.72,
            "adversarial_surface": 0.66,
            "relationship_value": 0.58,
            "ground_truth": 0.55,
            "strategic_depth": 0.62,
            "noise_resistance": 0.62,
        },
        "Social Media Agent": {
            "breadth": 0.62,
            "timeliness": 0.95,
            "provenance": 0.28,
            "influence_surface": 0.98,
            "adversarial_surface": 0.92,
            "relationship_value": 0.64,
            "ground_truth": 0.32,
            "strategic_depth": 0.38,
            "noise_resistance": 0.32,
        },
        "Public Records Agent": {
            "breadth": 0.48,
            "timeliness": 0.38,
            "provenance": 0.96,
            "influence_surface": 0.22,
            "adversarial_surface": 0.42,
            "relationship_value": 0.86,
            "ground_truth": 0.82,
            "strategic_depth": 0.82,
            "noise_resistance": 0.88,
        },
        "Academic / Research Agent": {
            "breadth": 0.52,
            "timeliness": 0.26,
            "provenance": 0.88,
            "influence_surface": 0.30,
            "adversarial_surface": 0.36,
            "relationship_value": 0.58,
            "ground_truth": 0.72,
            "strategic_depth": 0.90,
            "noise_resistance": 0.82,
        },
        "Video / Media Agent": {
            "breadth": 0.50,
            "timeliness": 0.72,
            "provenance": 0.50,
            "influence_surface": 0.85,
            "adversarial_surface": 0.78,
            "relationship_value": 0.62,
            "ground_truth": 0.70,
            "strategic_depth": 0.45,
            "noise_resistance": 0.48,
        },
        "Forum Agent": {
            "breadth": 0.58,
            "timeliness": 0.80,
            "provenance": 0.32,
            "influence_surface": 0.70,
            "adversarial_surface": 0.88,
            "relationship_value": 0.70,
            "ground_truth": 0.36,
            "strategic_depth": 0.56,
            "noise_resistance": 0.38,
        },
        "Geospatial / Imagery Agent": {
            "breadth": 0.38,
            "timeliness": 0.62,
            "provenance": 0.78,
            "influence_surface": 0.36,
            "adversarial_surface": 0.46,
            "relationship_value": 0.80,
            "ground_truth": 0.96,
            "strategic_depth": 0.70,
            "noise_resistance": 0.78,
        },
    }


def fusion_matrix(modality_weighting: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    mission_vectors: dict[str, dict[str, float]] = {
        "General Intelligence": {
            "breadth": 0.22,
            "timeliness": 0.14,
            "provenance": 0.16,
            "influence_surface": 0.08,
            "adversarial_surface": 0.08,
            "relationship_value": 0.12,
            "ground_truth": 0.10,
            "strategic_depth": 0.10,
        },
        "Influence Operations": {
            "breadth": 0.07,
            "timeliness": 0.15,
            "provenance": 0.08,
            "influence_surface": 0.32,
            "adversarial_surface": 0.18,
            "relationship_value": 0.10,
            "ground_truth": 0.04,
            "strategic_depth": 0.06,
        },
        "Information Warfare": {
            "breadth": 0.08,
            "timeliness": 0.15,
            "provenance": 0.10,
            "influence_surface": 0.22,
            "adversarial_surface": 0.23,
            "relationship_value": 0.09,
            "ground_truth": 0.08,
            "strategic_depth": 0.05,
        },
        "Competitive Intelligence": {
            "breadth": 0.10,
            "timeliness": 0.08,
            "provenance": 0.25,
            "influence_surface": 0.03,
            "adversarial_surface": 0.05,
            "relationship_value": 0.23,
            "ground_truth": 0.10,
            "strategic_depth": 0.16,
        },
        "National Security Monitoring": {
            "breadth": 0.09,
            "timeliness": 0.14,
            "provenance": 0.16,
            "influence_surface": 0.08,
            "adversarial_surface": 0.17,
            "relationship_value": 0.15,
            "ground_truth": 0.14,
            "strategic_depth": 0.07,
        },
        "Crisis Monitoring": {
            "breadth": 0.08,
            "timeliness": 0.28,
            "provenance": 0.10,
            "influence_surface": 0.13,
            "adversarial_surface": 0.11,
            "relationship_value": 0.08,
            "ground_truth": 0.18,
            "strategic_depth": 0.04,
        },
        "Strategic Warning": {
            "breadth": 0.08,
            "timeliness": 0.11,
            "provenance": 0.18,
            "influence_surface": 0.05,
            "adversarial_surface": 0.12,
            "relationship_value": 0.20,
            "ground_truth": 0.13,
            "strategic_depth": 0.13,
        },
    }
    attrs = modality_attributes()
    # Extra trust penalty for modalities whose own workflow weighting requires
    # unusually heavy noise filtering; this keeps social/forum data important
    # for relevant missions without making it over-trusted.
    matrix_by_mission: dict[str, dict[str, float]] = {}
    for mission, vector in mission_vectors.items():
        raw: dict[str, float] = {}
        for modality in MODALITIES:
            capability = sum(attrs[modality][attribute] * factor for attribute, factor in vector.items())
            noise_drag = modality_weighting[modality]["filter_noise"] / 100.0
            confidence_bonus = modality_weighting[modality]["assess_confidence"] / 250.0
            adjusted = max(0.01, capability * (1 - 0.22 * noise_drag) + confidence_bonus)
            raw[modality] = adjusted**1.8
        matrix_by_mission[mission] = normalize(raw)
    # Transpose to modality -> mission for reporting.
    return {
        modality: {mission: matrix_by_mission[mission][modality] for mission in MISSION_CONDITIONS}
        for modality in MODALITIES
    }


def final_tracegrid_weights(
    global_metrics: dict[str, dict[str, float]],
    recovery: dict[str, dict[str, float | str]],
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    failure_impact = {step: global_metrics[step]["average"] for step, _label in STEPS}
    failure_frequency_component = {
        step: min(
            4.0,
            4
            * (
                global_metrics[step]["failure_frequency"] * 0.50
                + global_metrics[step]["major_failure_frequency"] * 0.35
                + global_metrics[step]["catastrophic_frequency"] * 0.15
            ),
        )
        for step, _label in STEPS
    }
    recoverability_component = {step: float(recovery[step]["recoverability_score"]) for step, _label in STEPS}
    raw = {
        step: 0.40 * failure_impact[step]
        + 0.30 * failure_frequency_component[step]
        + 0.30 * recoverability_component[step]
        for step, _label in STEPS
    }
    normalized = normalize(raw)
    components = {
        step: {
            "failure_impact_component": round(failure_impact[step], 4),
            "failure_frequency_component": round(failure_frequency_component[step], 4),
            "recoverability_component": round(recoverability_component[step], 4),
            "raw_composite": round(raw[step], 4),
            "normalized_weight": normalized[step],
        }
        for step, _label in STEPS
    }
    return normalized, components


def write_phase2_failure_impact(
    generated: str,
    global_metrics: dict[str, dict[str, float]],
    profession_metrics: dict[str, dict[str, dict[str, float]]],
) -> None:
    sections = [
        "# Phase II Study A: Failure Impact Analysis",
        "",
        f"Generated: {generated}",
        "",
        "## Scope",
        "",
        "Observed analysis from the existing Phase I corpus only. Impact scores are the per-step `*_impact_score` fields from `case_studies.csv`.",
        "",
        "## Global impact metrics",
        "",
        table(
            ["Workflow step", "Average impact", "Median", "Std dev", "Catastrophic frequency"],
            [
                [
                    label,
                    global_metrics[step]["average"],
                    global_metrics[step]["median"],
                    global_metrics[step]["stdev"],
                    global_metrics[step]["catastrophic_frequency"],
                ]
                for step, label in STEPS
            ],
        ),
        "",
        "## Profession-specific impact rankings",
        "",
    ]
    for profession in PROFESSIONS:
        sections.append(f"### {profession}")
        sections.append("")
        sections.append(
            table(
                ["Rank", "Workflow step", "Average", "Median", "Std dev", "Catastrophic frequency"],
                [
                    [
                        rank,
                        label,
                        profession_metrics[profession][step]["average"],
                        profession_metrics[profession][step]["median"],
                        profession_metrics[profession][step]["stdev"],
                        profession_metrics[profession][step]["catastrophic_frequency"],
                    ]
                    for rank, (label, _value) in enumerate(ranking(profession_metrics[profession]), start=1)
                    for step, step_label in STEPS
                    if step_label == label
                ],
            )
        )
        sections.append("")
    sections.extend(
        [
            "## Skeptical reading",
            "",
            "- These are observed corpus scores, but the Phase I scores were proxy-coded from public catalogs. They are not independent expert judgments.",
            "- Catastrophic failures are sparse in the corpus and are concentrated in the NOAA/weather and market-signal portions, so catastrophic-frequency comparisons should be treated as tail-risk indicators rather than stable rates.",
            "- The most defensible architectural use is rank ordering and stress testing, not fine-grained percentage precision.",
        ]
    )
    (ROOT / "phase2_failure_impact.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_phase2_failure_frequency(
    generated: str,
    global_metrics: dict[str, dict[str, float]],
    profession_metrics: dict[str, dict[str, dict[str, float]]],
) -> None:
    sections = [
        "# Phase II Study B: Failure Frequency Analysis",
        "",
        f"Generated: {generated}",
        "",
        "## Definitions",
        "",
        "- **Failure occurrence frequency:** share of rows where the step impact score is greater than 0.",
        "- **Major failure frequency:** share of rows where the step impact score is 3 or 4.",
        "- **Catastrophic failure frequency:** share of rows where the step impact score is 4.",
        "",
        "## Global frequency metrics",
        "",
        table(
            ["Workflow step", "Occurrence frequency", "Major frequency", "Catastrophic frequency", "Failure count", "Major count", "Catastrophic count"],
            [
                [
                    label,
                    global_metrics[step]["failure_frequency"],
                    global_metrics[step]["major_failure_frequency"],
                    global_metrics[step]["catastrophic_frequency"],
                    int(global_metrics[step]["failure_count"]),
                    int(global_metrics[step]["major_failure_count"]),
                    int(global_metrics[step]["catastrophic_count"]),
                ]
                for step, label in STEPS
            ],
        ),
        "",
        "## Profession-specific frequency tables",
        "",
    ]
    for profession in PROFESSIONS:
        sections.append(f"### {profession}")
        sections.append("")
        sections.append(
            table(
                ["Workflow step", "Occurrence frequency", "Major frequency", "Catastrophic frequency"],
                [
                    [
                        label,
                        profession_metrics[profession][step]["failure_frequency"],
                        profession_metrics[profession][step]["major_failure_frequency"],
                        profession_metrics[profession][step]["catastrophic_frequency"],
                    ]
                    for step, label in STEPS
                ],
            )
        )
        sections.append("")
    sections.extend(
        [
            "## Observed pattern",
            "",
            "The corpus separates frequent weakness from catastrophic weakness. Confidence assessment and signal collection fail often; catastrophic failures are rarer and should be interpreted as high-consequence tails rather than everyday events.",
            "",
            "## Limitation",
            "",
            "Because Phase I final-output quality is derived from step scores, failure frequency is not a causal estimate. It is a workload/architecture pressure estimate: where TraceGrid should expect recurring control burden.",
        ]
    )
    (ROOT / "phase2_failure_frequency.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_phase2_recoverability(
    generated: str,
    rows: list[dict[str, str]],
    recovery_global: dict[str, dict[str, float | str]],
) -> None:
    by_prof = {profession: recoverability_scores(rows, profession) for profession in PROFESSIONS}
    sections = [
        "# Phase II Study C: Recoverability Analysis",
        "",
        f"Generated: {generated}",
        "",
        "## Status of this analysis",
        "",
        "**Inferred architectural model, not directly observed counterfactual evidence.** The Phase I corpus records failed/weak steps and degraded outputs, but it does not run alternate histories where downstream stages repair upstream failures. This study therefore blends:",
        "",
        "1. a declared workflow-structure prior, and",
        "2. observed Phase I failure propagation, major-failure rate, catastrophic-failure rate, downstream burden, and downstream-clean rate.",
        "",
        "## Recovery scale",
        "",
        table(["Score band", "Meaning"], [["0", "Fully Recoverable"], ["1", "Mostly Recoverable"], ["2", "Partially Recoverable"], ["3", "Rarely Recoverable"], ["4", "Not Recoverable"]]),
        "",
        "## Global recoverability model",
        "",
        table(
            [
                "Workflow step",
                "Recoverability score",
                "Recovery label",
                "Structural prior",
                "Observed non-recovery",
                "Major given failure",
                "Downstream clean rate",
            ],
            [
                [
                    label,
                    recovery_global[step]["recoverability_score"],
                    recovery_global[step]["recoverability_label"],
                    recovery_global[step]["structural_prior"],
                    recovery_global[step]["observed_non_recovery"],
                    recovery_global[step]["major_given_failure"],
                    recovery_global[step]["downstream_clean_rate"],
                ]
                for step, label in STEPS
            ],
        ),
        "",
        "## Profession-specific recoverability scores",
        "",
    ]
    for profession in PROFESSIONS:
        sections.append(f"### {profession}")
        sections.append("")
        sections.append(
            table(
                ["Workflow step", "Recoverability score", "Recovery label", "Observed non-recovery"],
                [
                    [
                        label,
                        by_prof[profession][step]["recoverability_score"],
                        by_prof[profession][step]["recoverability_label"],
                        by_prof[profession][step]["observed_non_recovery"],
                    ]
                    for step, label in STEPS
                ],
            )
        )
        sections.append("")
    sections.extend(
        [
            "## Interpretation",
            "",
            "- **Collect Signals** is modeled as the least recoverable step. If evidence was never collected, later corroboration and confidence scoring mostly operate on absence, not evidence.",
            "- **Assess Confidence** is rarely recoverable because an overconfident or underconfident handoff contaminates downstream decisions even if the evidence exists.",
            "- **Map Relationships** is partially recoverable when evidence/provenance remains intact; analysts can rebuild graph structure after the fact.",
            "- **Produce Understanding** is the most recoverable step because a bad report or handoff can often be rewritten if evidence, provenance, and confidence state remain intact.",
            "",
            "## Human adjudication needed",
            "",
            "A stronger Phase III design should sample high-impact rows and ask domain experts whether actual recovery occurred: Was missing collection repaired by later collection? Did confidence calibration prevent misuse? Did relationship mapping errors propagate to decision makers?",
        ]
    )
    (ROOT / "phase2_recoverability.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_modality_weighting(generated: str, weights: dict[str, dict[str, float]]) -> None:
    sections = [
        "# Phase II Study D: Information Modality Dependency Analysis",
        "",
        f"Generated: {generated}",
        "",
        "## Status of this analysis",
        "",
        "Mixed observed/inferred architecture model. Phase I professions map imperfectly to TraceGrid collection media, so modality weights blend observed profession weights, global recoverability, and declared medium-specific dependency priors.",
        "",
        "## Modality-specific weighting tables",
        "",
    ]
    for modality in MODALITIES:
        sections.append(f"### {modality}")
        sections.append("")
        sections.append(
            table(
                ["Workflow step", "Weight %"],
                [[label, weights[modality][step]] for step, label in STEPS],
            )
        )
        sections.append("")
    variation = {
        step: statistics.pstdev([weights[modality][step] for modality in MODALITIES]) for step, _label in STEPS
    }
    sections.extend(
        [
            "## Cross-modality variation",
            "",
            table(
                ["Workflow step", "Std dev across modalities", "Interpretation"],
                [
                    [
                        label,
                        round(variation[step], 2),
                        "Highly medium-sensitive" if variation[step] >= 3 else "Moderately variable" if variation[step] >= 1.5 else "Relatively universal",
                    ]
                    for step, label in STEPS
                ],
            ),
            "",
            "## Design implication",
            "",
            "TraceGrid should not use one collection-agent weighting profile. Social, forum, video, and web-search agents need heavier noise/corroboration controls; public-records and geospatial agents need stronger observation, relationship mapping, provenance, and confidence preservation.",
        ]
    )
    (ROOT / "modality_weighting.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_fusion_matrix(generated: str, matrix: dict[str, dict[str, float]]) -> None:
    sections = [
        "# Phase II Study E: Axiom Forge Fusion Trust Matrix",
        "",
        f"Generated: {generated}",
        "",
        "## Status of this analysis",
        "",
        "Inferred Conductor-operations model. The matrix normalizes trust allocation across modalities for each mission condition. It combines modality capability attributes with each modality's workflow burden, including a trust penalty for high noise-filtering dependency.",
        "",
        "## Fusion trust matrix",
        "",
        table(
            ["Modality"] + MISSION_CONDITIONS,
            [
                [modality] + [matrix[modality][mission] for mission in MISSION_CONDITIONS]
                for modality in MODALITIES
            ],
        ),
        "",
        "Each mission column sums to 100%. These are not source-truth probabilities; they are orchestration priors for how Axiom Forge should allocate attention, contradiction checks, and confidence mass before case-specific evidence is evaluated.",
        "",
        "## Fusion guidance",
        "",
        "- **General Intelligence:** start broad; use web/news for coverage, then public records, academic, and geospatial for stabilization.",
        "- **Influence Operations:** social, video/media, forums, and news deserve higher attention, but never high standalone trust without corroboration.",
        "- **Information Warfare:** treat social/forum/media as high-signal but adversarial; fuse with news and geospatial for grounding.",
        "- **Competitive Intelligence:** public records should anchor trust; news/web search provide timeliness and context.",
        "- **National Security Monitoring:** geospatial, news, public records, and forums/social should be fused with explicit contradiction tracking.",
        "- **Crisis Monitoring:** timeliness dominates early; news/social/geospatial/video should be weighted heavily but confidence should remain provisional.",
        "- **Strategic Warning:** public records, geospatial, academic/research, forums, and news provide complementary slow/early indicators.",
        "",
        "## StratSight handoff requirement",
        "",
        "Axiom Forge should hand StratSight not only fused conclusions but also per-modality confidence, contradiction state, provenance coverage, and which modality would most change the estimate if updated.",
    ]
    (ROOT / "axiom_forge_fusion_matrix.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_final_weighting(
    generated: str,
    final_weights: dict[str, float],
    components: dict[str, dict[str, float]],
) -> None:
    sections = [
        "# TraceGrid Final Phase II Weighting Model",
        "",
        f"Generated: {generated}",
        "",
        "## Composite formula",
        "",
        "`Final Step Weight = (0.40 x Failure Impact) + (0.30 x Failure Frequency) + (0.30 x Recoverability)`",
        "",
        "Failure Impact and Failure Frequency are observed from the Phase I corpus. Recoverability is inferred from workflow structure plus observed failure propagation. The raw composite is normalized to 100%.",
        "",
        "## Final global TraceGrid weighting",
        "",
        table(
            ["Workflow step", "Failure impact component", "Failure frequency component", "Recoverability component", "Raw composite", "Final weight %"],
            [
                [
                    label,
                    components[step]["failure_impact_component"],
                    components[step]["failure_frequency_component"],
                    components[step]["recoverability_component"],
                    components[step]["raw_composite"],
                    final_weights[step],
                ]
                for step, label in STEPS
            ],
        ),
        "",
        "## Recommended architecture priority",
        "",
    ]
    for rank, (step, weight) in enumerate(sorted(final_weights.items(), key=lambda item: item[1], reverse=True), start=1):
        label = dict(STEPS)[step]
        sections.append(f"{rank}. **{label}** - {weight}%")
    sections.extend(
        [
            "",
            "## Interpretation",
            "",
            "The Phase II model shifts architectural emphasis away from a pure observed-frequency view and toward non-recoverable evidence operations. Collection, confidence assessment, corroboration, and relationship mapping form the core TraceGrid architecture. Produce Understanding remains important for decision handoff, but it should not receive the same infrastructure weight as evidence capture and confidence preservation because it is more recoverable when upstream state is intact.",
        ]
    )
    (ROOT / "tracegrid_final_weighting.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_executive_summary(
    generated: str,
    rows: list[dict[str, str]],
    global_metrics: dict[str, dict[str, float]],
    final_weights: dict[str, float],
    recovery: dict[str, dict[str, float | str]],
    modality: dict[str, dict[str, float]],
    fusion: dict[str, dict[str, float]],
) -> None:
    modality_variation = {
        step: statistics.pstdev([modality[mod][step] for mod in MODALITIES]) for step, _label in STEPS
    }
    most_important = max(final_weights, key=final_weights.get)
    least_recoverable = max(recovery, key=lambda step: float(recovery[step]["recoverability_score"]))
    largest_cat = max(global_metrics, key=lambda step: (global_metrics[step]["catastrophic_frequency"], global_metrics[step]["average"]))
    most_variable = max(modality_variation, key=modality_variation.get)
    most_universal = min(modality_variation, key=modality_variation.get)
    source_counts = Counter(row["source_catalog"] for row in rows)
    phase_i_counts = Counter(row["profession"] for row in rows)
    sections = [
        "# Phase II Executive Summary",
        "",
        f"Generated: {generated}",
        "",
        "## Corpus used",
        "",
        f"Phase II used the existing Phase I corpus only: {len(rows):,} rows from `case_studies.csv`. The dataset was not regenerated.",
        "",
        table(["Profession", "Rows"], [[profession, phase_i_counts[profession]] for profession in PROFESSIONS]),
        "",
        table(["Source catalog", "Rows"], [[source, count] for source, count in source_counts.items()]),
        "",
        "## Direct answers",
        "",
        f"1. **Most important global workflow step:** {dict(STEPS)[most_important]} ({final_weights[most_important]}% final Phase II weight).",
        f"2. **Least recoverable step:** {dict(STEPS)[least_recoverable]} ({recovery[least_recoverable]['recoverability_label']}, score {recovery[least_recoverable]['recoverability_score']}).",
        f"3. **Largest catastrophic failures:** {dict(STEPS)[largest_cat]} (catastrophic frequency {global_metrics[largest_cat]['catastrophic_frequency']}; average impact {global_metrics[largest_cat]['average']}).",
        f"4. **Step varying most by modality:** {dict(STEPS)[most_variable]} (std dev {modality_variation[most_variable]:.2f} percentage points).",
        f"5. **Most universal step by modality:** {dict(STEPS)[most_universal]} (lowest std dev {modality_variation[most_universal]:.2f} percentage points).",
        "6. **Weighting TraceGrid should use:**",
        "",
        table(["Workflow step", "Final weight %"], [[label, final_weights[step]] for step, label in STEPS]),
        "",
        "7. **Weighting each collection agent should use:** see `modality_weighting.md`; summarized below by each agent's top three controls.",
        "",
        table(
            ["Agent", "Top workflow controls"],
            [
                [
                    mod,
                    "; ".join(
                        f"{dict(STEPS)[step]} ({weight}%)"
                        for step, weight in sorted(modality[mod].items(), key=lambda item: item[1], reverse=True)[:3]
                    ),
                ]
                for mod in MODALITIES
            ],
        ),
        "",
        "8. **How Axiom Forge should fuse modality outputs:** use mission-specific trust priors, not a single universal modality ranking. Highest-weight modalities by mission:",
        "",
        table(
            ["Mission", "Top modality trust priors"],
            [
                [
                    mission,
                    "; ".join(
                        f"{mod} ({fusion[mod][mission]}%)"
                        for mod in sorted(MODALITIES, key=lambda candidate: fusion[candidate][mission], reverse=True)[:3]
                    ),
                ]
                for mission in MISSION_CONDITIONS
            ],
        ),
        "",
        "9. **Architectural implications:**",
        "",
        "- Build an evidence/provenance substrate before optimizing dashboards.",
        "- Treat collection completeness as a hard dependency; absent signals are rarely recoverable.",
        "- Make confidence assessment a first-class, versioned object rather than a prose afterthought.",
        "- Build corroboration and contradiction detection as core services.",
        "- Maintain relationship graphs as operational state, not optional visualization.",
        "- Give each modality its own noise/corroboration/confidence policy.",
        "- Make Axiom Forge fusion mission-aware and uncertainty-preserving.",
        "- Hand StratSight evidence bundles with provenance, graph slice, confidence, contradiction state, and decision thresholds.",
        "",
        "10. **MVP priorities:**",
        "",
        "1. Source/evidence capture with immutable provenance",
        "2. Collection completeness and coverage tracking",
        "3. Corroboration/contradiction engine",
        "4. Confidence scoring and calibration ledger",
        "5. Relationship graph/entity resolution",
        "6. Modality-specific filtering profiles",
        "7. Axiom Forge fusion matrix and StratSight handoff schema",
        "8. Analyst explanation layer",
        "",
        "## Doctrine validation",
        "",
        "> TraceGrid is not fundamentally an OSINT platform. TraceGrid is infrastructure for transforming uncertainty into defensible confidence through a structured epistemological workflow.",
        "",
        "**Assessment: supported, with limits.**",
        "",
        "The evidence supports the doctrine because the strongest Phase II architecture weights do not merely reward finding more online sources. The final model prioritizes collection integrity, confidence assessment, corroboration, and relationship mapping: the functions that turn uncertain observations into claims that can survive audit and decision handoff. The modality analysis also supports the doctrine: news, social, public records, forums, imagery, and academic material require different collection policies, but they converge on the same epistemological controls.",
        "",
        "The falsification attempt is important: if TraceGrid were simply an OSINT platform, source discovery and collection volume would dominate. They do not. Collection remains high because missing evidence is least recoverable, but standalone observation/discovery and final report production are not sufficient. The architecture must preserve provenance, expose uncertainty, and fuse contradictory evidence.",
        "",
        "The doctrine is not proven as a universal law. The Phase I corpus is proxy-coded, not expert-adjudicated; social, forum, academic, video, and geospatial modality weights are partly inferred; and recovery is counterfactual. Human adjudication is required before treating the numeric weights as stable production defaults. Still, for architectural prioritization, the doctrine is more defensible than an OSINT-platform framing.",
        "",
        "## Observed vs inferred findings",
        "",
        "- **Observed from corpus:** impact averages, medians, standard deviations, failure frequencies, major/catastrophic frequencies, profession rankings.",
        "- **Inferred from observed corpus plus workflow priors:** recoverability scores and final composite weighting.",
        "- **Inferred for architecture:** modality-specific agent weights and Axiom Forge fusion trust matrix.",
        "",
        "## Limitations requiring human adjudication",
        "",
        "- Phase I rows are real and cited but mostly proxy-coded from metadata.",
        "- Failure scores and final-output quality are not independent variables.",
        "- Recoverability is not directly observed; it should be tested with expert counterfactual review.",
        "- Social media, forums, academic research, video/media, and geospatial agents need dedicated native corpora.",
        "- Mission-specific fusion weights should be calibrated against real Axiom Forge task outcomes.",
    ]
    (ROOT / "phase2_executive_summary.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_rows()
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    global_metrics, profession_metrics = grouped_metrics(rows)
    profession_weights = {profession: step_weight_from_metrics(profession_metrics[profession]) for profession in PROFESSIONS}
    global_observed_weights = step_weight_from_metrics(global_metrics)
    recovery = recoverability_scores(rows)
    modality = modality_weights(global_observed_weights, profession_weights, recovery)
    fusion = fusion_matrix(modality)
    final_weights, components = final_tracegrid_weights(global_metrics, recovery)

    write_phase2_failure_impact(generated, global_metrics, profession_metrics)
    write_phase2_failure_frequency(generated, global_metrics, profession_metrics)
    write_phase2_recoverability(generated, rows, recovery)
    write_modality_weighting(generated, modality)
    write_fusion_matrix(generated, fusion)
    write_final_weighting(generated, final_weights, components)
    write_executive_summary(generated, rows, global_metrics, final_weights, recovery, modality, fusion)

    print(f"Read {len(rows)} existing Phase I rows from {CASE_CSV}")
    print("Wrote Phase II markdown deliverables")
    print("Final weights:", final_weights)


if __name__ == "__main__":
    main()
