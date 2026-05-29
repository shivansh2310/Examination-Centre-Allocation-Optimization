import math
import random

from .config import DATA_DIR, DISTRICTS
from .io_utils import ensure_dirs, write_csv


def district_centroids() -> dict[str, tuple[float, float]]:
    centroids: dict[str, tuple[float, float]] = {}
    for idx in range(1, 6):
        centroids[f"North_{idx}"] = (180 + idx * 115, 820 + ((idx % 2) * 35))
        centroids[f"South_{idx}"] = (180 + idx * 115, 180 - ((idx % 2) * 30))
        centroids[f"East_{idx}"] = (820 + ((idx % 2) * 35), 180 + idx * 115)
    for idx in range(1, 5):
        centroids[f"West_{idx}"] = (180 - ((idx % 2) * 30), 220 + idx * 140)
    centroids["Metro"] = (500, 500)
    return centroids


def _clip(value: float, low: float = 0, high: float = 1000) -> float:
    return max(low, min(high, value))


def _jitter(point: tuple[float, float], rng: random.Random, spread: float) -> tuple[float, float]:
    x, y = point
    return (_clip(rng.gauss(x, spread)), _clip(rng.gauss(y, spread)))


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _weighted_sample_without_replacement(
    items: list[dict], weights: list[float], k: int, rng: random.Random
) -> list[dict]:
    available = list(zip(items, weights, strict=True))
    chosen = []
    for _ in range(k):
        total = sum(weight for _, weight in available)
        pick = rng.uniform(0, total)
        cumulative = 0.0
        for index, (item, weight) in enumerate(available):
            cumulative += weight
            if cumulative >= pick:
                chosen.append(item)
                del available[index]
                break
    return chosen


def generate_environment(
    num_students: int = 2000,
    seed: int = 42,
    output_dir=DATA_DIR,
) -> tuple[list[dict], list[dict], list[dict]]:
    rng = random.Random(seed)
    ensure_dirs(output_dir)
    centroids = district_centroids()

    centres = []
    for index, district in enumerate(DISTRICTS, start=1):
        x, y = _jitter(centroids[district], rng, spread=28)
        transport_quality = rng.randint(1, 10)
        food_availability = rng.randint(1, 10)
        accommodation_availability = rng.randint(1, 10)
        centres.append(
            {
                "centre_id": f"C{index:03d}",
                "district": district,
                "x": round(x, 3),
                "y": round(y, 3),
                "capacity": rng.randint(200, 500),
                "transport_quality": transport_quality,
                "food_availability": food_availability,
                "accommodation_availability": accommodation_availability,
            }
        )

    students = []
    district_weights = [1.6 if district == "Metro" else 1.0 for district in DISTRICTS]
    for index in range(1, num_students + 1):
        district = rng.choices(DISTRICTS, weights=district_weights, k=1)[0]
        x, y = _jitter(centroids[district], rng, spread=45)
        students.append(
            {
                "student_id": f"S{index:05d}",
                "district": district,
                "x": round(x, 3),
                "y": round(y, 3),
                "gender": rng.choice(["M", "F"]),
            }
        )

    preferences = []
    for student in students:
        student_point = (float(student["x"]), float(student["y"]))
        weights = []
        for centre in centres:
            centre_point = (float(centre["x"]), float(centre["y"]))
            weights.append(1 / ((_distance(student_point, centre_point) + 25) ** 1.7))
        chosen = _weighted_sample_without_replacement(centres, weights, 3, rng)
        preferences.append(
            {
                "student_id": student["student_id"],
                "pref_1": chosen[0]["centre_id"],
                "pref_2": chosen[1]["centre_id"],
                "pref_3": chosen[2]["centre_id"],
            }
        )

    write_csv(output_dir / "students.csv", students)
    write_csv(output_dir / "centres.csv", centres)
    write_csv(output_dir / "preferences.csv", preferences)
    return students, centres, preferences
