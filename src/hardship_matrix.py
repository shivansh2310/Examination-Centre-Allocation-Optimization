from .config import DATA_DIR, DEFAULT_WEIGHTS
from .distance_matrix import build_distance_matrix
from .io_utils import read_csv, write_csv


PREFERENCE_PENALTIES = {"pref_1": 0, "pref_2": 5, "pref_3": 10}
OUTSIDE_PREFERENCE_PENALTY = 50


def centre_accessibility_penalties(centres: list[dict]) -> dict[str, float]:
    penalties = {}
    for centre in centres:
        score = (
            float(centre["transport_quality"])
            + float(centre["food_availability"])
            + float(centre["accommodation_availability"])
        ) / 3
        penalties[centre["centre_id"]] = 10 - score
    return penalties


def preference_penalty(preference: dict, centre_id: str) -> int:
    for key, penalty in PREFERENCE_PENALTIES.items():
        if preference[key] == centre_id:
            return penalty
    return OUTSIDE_PREFERENCE_PENALTY


def build_hardship_matrix(
    alpha: float = DEFAULT_WEIGHTS["alpha"],
    beta: float = DEFAULT_WEIGHTS["beta"],
    lambda_: float = DEFAULT_WEIGHTS["lambda_"],
    students: list[dict] | None = None,
    centres: list[dict] | None = None,
    preferences: list[dict] | None = None,
    distances: list[dict] | None = None,
    output_path=DATA_DIR / "hardship_matrix.csv",
) -> list[dict]:
    students = students if students is not None else read_csv(DATA_DIR / "students.csv")
    centres = centres if centres is not None else read_csv(DATA_DIR / "centres.csv")
    preferences = preferences if preferences is not None else read_csv(DATA_DIR / "preferences.csv")
    distances = distances if distances is not None else build_distance_matrix(students, centres)

    preference_by_student = {row["student_id"]: row for row in preferences}
    accessibility_penalty_by_centre = centre_accessibility_penalties(centres)
    rows = []
    for row in distances:
        distance = float(row["distance"])
        centre_id = row["centre_id"]
        student_id = row["student_id"]
        accessibility_penalty = accessibility_penalty_by_centre[centre_id]
        pref_penalty = preference_penalty(preference_by_student[student_id], centre_id)
        hardship = alpha * distance + beta * accessibility_penalty + lambda_ * pref_penalty
        rows.append(
            {
                "student_id": student_id,
                "centre_id": centre_id,
                "distance": round(distance, 3),
                "accessibility_penalty": round(accessibility_penalty, 3),
                "preference_penalty": pref_penalty,
                "hardship": round(hardship, 3),
            }
        )
    write_csv(output_path, rows)
    return rows
