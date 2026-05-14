import csv
import json
import os
import uuid

from artifact_loop.models import RawSpec
from artifact_loop.high_architect import HighArchitectStage

SPECS = [
    (
        "spec_01_underspecified",
        "Build a family budgeting app for WhatsApp.",
    ),
    (
        "spec_02_contradictory",
        "I want a private messaging system where all messages are publicly searchable.",
    ),
    (
        "spec_03_non_crud_workflow",
        "Create a classroom AI tutor that adapts question difficulty based on student frustration.",
    ),
    (
        "spec_04_operational_system",
        (
            "Build a warehouse monitoring system that alerts managers when refrigeration units "
            "drift outside safe temperature ranges."
        ),
    ),
    (
        "spec_05_multi_actor",
        (
            "Create a marketplace connecting freelance music teachers and students "
            "with recurring lessons and ratings."
        ),
    ),
    (
        "spec_06_intentionally_vague",
        "I want an AI second brain for my life.",
    ),
    (
        "spec_07_edge_case_constraints",
        (
            "Build a scheduling system for therapists where client anonymity must be "
            "preserved across all notifications."
        ),
    ),
]

RESULTS_BASE = os.path.join(
    os.path.dirname(__file__), "..", "results", "hld_stress_suite"
)

COL_WIDTHS = {
    "name": 32,
    "attempts": 8,
    "status": 10,
    "converged": 9,
    "final_risk": 10,
    "blocking": 8,
    "hallucinations": 14,
    "preservation": 13,
    "convergence": 11,
}

HEADERS = list(COL_WIDTHS.keys())


def fmt_row(values: list) -> str:
    cells = [str(v).ljust(COL_WIDTHS[h]) for h, v in zip(HEADERS, values)]
    return " | ".join(cells)


def main():
    run_id = str(uuid.uuid4())
    results_dir = os.path.join(RESULTS_BASE, run_id)
    os.makedirs(results_dir, exist_ok=True)
    print(f"Run ID: {run_id}")

    stage = HighArchitectStage(threshold=0.95, risk_threshold=0.35, max_attempts=3)

    rows = []

    for slug, spec_text in SPECS:
        print(f"\n>>> Running {slug} ...")
        raw = RawSpec(text=spec_text)
        result = stage.run(raw)

        out_path = os.path.join(results_dir, f"{slug}.json")
        with open(out_path, "w") as f:
            json.dump(result.model_dump(), f, indent=2)
        print(f"    Saved → {out_path}")

        m = result.run_convergence
        lm = result.attempts[-1].metrics

        rows.append([
            slug,
            m.attempts,
            m.status,
            m.converged,
            round(m.final_risk_score, 3),
            lm.blocking_failure,
            lm.hallucination_count,
            round(lm.preservation_score, 3),
            round(m.convergence_score, 4),
        ])

    print("\n\n=== HLD STRESS SUITE SUMMARY ===\n")
    separator = "-" * (sum(COL_WIDTHS.values()) + 3 * (len(HEADERS) - 1))
    print(fmt_row(HEADERS))
    print(separator)
    for row in rows:
        print(fmt_row(row))
    print()

    csv_path = os.path.join(results_dir, "summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(rows)
    print(f"Summary saved → {csv_path}")


if __name__ == "__main__":
    main()
