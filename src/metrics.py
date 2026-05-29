from collections import Counter

from .config import DATA_DIR, RESULTS_DIR
from .hardship_matrix import OUTSIDE_PREFERENCE_PENALTY, PREFERENCE_PENALTIES
from .io_utils import read_csv, write_csv


def calculate_metrics(
    assignments: list[dict],
    centres: list[dict] | None = None,
    preferences: list[dict] | None = None,
    hardship_rows: list[dict] | None = None,
    label: str = "allocation",
    output_path=None,
) -> dict:
    centres = centres if centres is not None else read_csv(DATA_DIR / "centres.csv")
    preferences = preferences if preferences is not None else read_csv(DATA_DIR / "preferences.csv")
    hardship_rows = hardship_rows if hardship_rows is not None else read_csv(DATA_DIR / "hardship_matrix.csv")
    output_path = output_path or RESULTS_DIR / f"{label}_metrics.csv"

    hardship_by_pair = {
        (row["student_id"], row["centre_id"]): row for row in hardship_rows
    }
    preferences_by_student = {row["student_id"]: row for row in preferences}
    capacities = {row["centre_id"]: int(row["capacity"]) for row in centres}

    distances = []
    hardships = []
    preference_counts = Counter()
    centre_counts = Counter()

    for assignment in assignments:
        student_id = assignment["student_id"]
        centre_id = assignment["centre_id"]
        matrix_row = hardship_by_pair[(student_id, centre_id)]
        distances.append(float(matrix_row["distance"]))
        hardships.append(float(matrix_row["hardship"]))
        centre_counts[centre_id] += 1

        preference = preferences_by_student[student_id]
        matched = "outside_preferences"
        for key, penalty in PREFERENCE_PENALTIES.items():
            if preference[key] == centre_id:
                matched = key
                break
        if matched == "outside_preferences":
            assert OUTSIDE_PREFERENCE_PENALTY >= 0
        preference_counts[matched] += 1

    total = len(assignments)
    utilization_rates = [
        centre_counts[centre_id] / capacity for centre_id, capacity in capacities.items()
    ]
    metrics = {
        "allocation": label,
        "assigned_students": total,
        "avg_distance": round(sum(distances) / total, 3),
        "max_distance": round(max(distances), 3),
        "first_preference_rate": round(preference_counts["pref_1"] / total, 4),
        "second_preference_rate": round(preference_counts["pref_2"] / total, 4),
        "third_preference_rate": round(preference_counts["pref_3"] / total, 4),
        "outside_preference_rate": round(preference_counts["outside_preferences"] / total, 4),
        "avg_hardship": round(sum(hardships) / total, 3),
        "avg_utilization_rate": round(sum(utilization_rates) / len(utilization_rates), 4),
        "max_utilization_rate": round(max(utilization_rates), 4),
    }
    write_csv(output_path, [metrics])
    return metrics


def validate_assignment(assignments: list[dict], students: list[dict], centres: list[dict]) -> None:
    student_ids = [row["student_id"] for row in students]
    assigned_ids = [row["student_id"] for row in assignments]
    if sorted(student_ids) != sorted(assigned_ids):
        raise ValueError("Assignment does not contain exactly one row for every student.")

    capacities = {row["centre_id"]: int(row["capacity"]) for row in centres}
    counts = Counter(row["centre_id"] for row in assignments)
    overfull = {
        centre_id: count
        for centre_id, count in counts.items()
        if count > capacities.get(centre_id, -1)
    }
    if overfull:
        raise ValueError(f"Capacity exceeded: {overfull}")
