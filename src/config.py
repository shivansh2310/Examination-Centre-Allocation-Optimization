from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
PLOTS_DIR = ROOT_DIR / "plots"

DISTRICTS = [
    "North_1",
    "North_2",
    "North_3",
    "North_4",
    "North_5",
    "South_1",
    "South_2",
    "South_3",
    "South_4",
    "South_5",
    "East_1",
    "East_2",
    "East_3",
    "East_4",
    "East_5",
    "West_1",
    "West_2",
    "West_3",
    "West_4",
    "Metro",
]

DEFAULT_WEIGHTS = {"alpha": 0.60, "beta": 0.20, "lambda_": 0.20}

SCENARIOS = {
    "distance_focused": {"alpha": 0.80, "beta": 0.10, "lambda_": 0.10},
    "preference_focused": {"alpha": 0.40, "beta": 0.10, "lambda_": 0.50},
    "accessibility_focused": {"alpha": 0.40, "beta": 0.50, "lambda_": 0.10},
    "balanced": DEFAULT_WEIGHTS,
}
