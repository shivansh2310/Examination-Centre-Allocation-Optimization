from .config import RESULTS_DIR, SCENARIOS
from .hardship_matrix import build_hardship_matrix
from .io_utils import write_csv
from .metrics import calculate_metrics, validate_assignment
from .optimizer import allocate_optimized


def run_sensitivity(
    students: list[dict],
    centres: list[dict],
    preferences: list[dict],
    distances: list[dict],
) -> list[dict]:
    rows = []
    for scenario, weights in SCENARIOS.items():
        hardship_rows = build_hardship_matrix(
            students=students,
            centres=centres,
            preferences=preferences,
            distances=distances,
            output_path=RESULTS_DIR / f"{scenario}_hardship_matrix.csv",
            **weights,
        )
        assignments = allocate_optimized(
            students=students,
            centres=centres,
            hardship_rows=hardship_rows,
            output_path=RESULTS_DIR / f"{scenario}_assignment.csv",
        )
        validate_assignment(assignments, students, centres)
        metrics = calculate_metrics(
            assignments,
            centres=centres,
            preferences=preferences,
            hardship_rows=hardship_rows,
            label=scenario,
            output_path=RESULTS_DIR / f"{scenario}_metrics.csv",
        )
        rows.append(metrics)
    write_csv(RESULTS_DIR / "sensitivity_results.csv", rows)
    return rows
