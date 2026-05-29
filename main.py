import argparse

from src.baseline_allocator import allocate_baseline
from src.config import DATA_DIR, PLOTS_DIR, RESULTS_DIR
from src.distance_matrix import build_distance_matrix
from src.generate_data import generate_environment
from src.hardship_matrix import build_hardship_matrix
from src.io_utils import ensure_dirs
from src.metrics import calculate_metrics, validate_assignment
from src.optimizer import allocate_optimized
from src.plots import create_plots
from src.sensitivity import run_sensitivity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Examination centre allocation optimization")
    parser.add_argument("--students", type=int, default=2000, help="Number of synthetic students")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for synthetic data")
    parser.add_argument(
        "--skip-sensitivity",
        action="store_true",
        help="Run only baseline and balanced optimized allocation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs(DATA_DIR, RESULTS_DIR, PLOTS_DIR)

    students, centres, preferences = generate_environment(
        num_students=args.students,
        seed=args.seed,
    )
    distances = build_distance_matrix(students, centres)
    hardship_rows = build_hardship_matrix(
        students=students,
        centres=centres,
        preferences=preferences,
        distances=distances,
    )

    baseline_assignment = allocate_baseline(students, centres)
    validate_assignment(baseline_assignment, students, centres)
    baseline_metrics = calculate_metrics(
        baseline_assignment,
        centres=centres,
        preferences=preferences,
        hardship_rows=hardship_rows,
        label="baseline",
        output_path=RESULTS_DIR / "baseline_metrics.csv",
    )

    optimized_assignment = allocate_optimized(students, centres, hardship_rows)
    validate_assignment(optimized_assignment, students, centres)
    optimized_metrics = calculate_metrics(
        optimized_assignment,
        centres=centres,
        preferences=preferences,
        hardship_rows=hardship_rows,
        label="optimized",
        output_path=RESULTS_DIR / "optimized_metrics.csv",
    )

    sensitivity_metrics = None
    if not args.skip_sensitivity:
        sensitivity_metrics = run_sensitivity(students, centres, preferences, distances)

    create_plots(baseline_metrics, optimized_metrics, sensitivity_metrics)

    print("Exam centre allocation project complete.")
    print(f"Students: {len(students)}")
    print(f"Baseline avg distance: {baseline_metrics['avg_distance']}")
    print(f"Optimized avg distance: {optimized_metrics['avg_distance']}")
    print(f"Baseline avg hardship: {baseline_metrics['avg_hardship']}")
    print(f"Optimized avg hardship: {optimized_metrics['avg_hardship']}")
    print(f"Results written to: {RESULTS_DIR}")
    print(f"Plots written to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
