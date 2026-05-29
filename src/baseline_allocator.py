import random

from .config import DATA_DIR, RESULTS_DIR
from .io_utils import read_csv, write_csv


def allocate_baseline(
    students: list[dict] | None = None,
    centres: list[dict] | None = None,
    seed: int = 99,
    output_path=RESULTS_DIR / "baseline_assignment.csv",
) -> list[dict]:
    students = students if students is not None else read_csv(DATA_DIR / "students.csv")
    centres = centres if centres is not None else read_csv(DATA_DIR / "centres.csv")

    if sum(int(centre["capacity"]) for centre in centres) < len(students):
        raise ValueError("Total centre capacity is smaller than the number of students.")

    rng = random.Random(seed)
    shuffled_students = students[:]
    shuffled_centres = centres[:]
    rng.shuffle(shuffled_students)
    rng.shuffle(shuffled_centres)

    assignments = []
    centre_index = 0
    remaining = int(shuffled_centres[centre_index]["capacity"])
    for student in shuffled_students:
        while remaining <= 0:
            centre_index += 1
            remaining = int(shuffled_centres[centre_index]["capacity"])
        centre = shuffled_centres[centre_index]
        assignments.append({"student_id": student["student_id"], "centre_id": centre["centre_id"]})
        remaining -= 1

    assignments.sort(key=lambda row: row["student_id"])
    write_csv(output_path, assignments)
    return assignments
