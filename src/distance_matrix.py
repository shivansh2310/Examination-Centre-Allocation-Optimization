import math

from .config import DATA_DIR
from .io_utils import read_csv, write_csv


def build_distance_matrix(
    students: list[dict] | None = None,
    centres: list[dict] | None = None,
    output_path=DATA_DIR / "distance_matrix.csv",
) -> list[dict]:
    students = students if students is not None else read_csv(DATA_DIR / "students.csv")
    centres = centres if centres is not None else read_csv(DATA_DIR / "centres.csv")

    rows = []
    for student in students:
        sx, sy = float(student["x"]), float(student["y"])
        for centre in centres:
            cx, cy = float(centre["x"]), float(centre["y"])
            rows.append(
                {
                    "student_id": student["student_id"],
                    "centre_id": centre["centre_id"],
                    "distance": round(math.hypot(sx - cx, sy - cy), 3),
                }
            )
    write_csv(output_path, rows)
    return rows
