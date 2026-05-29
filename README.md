# Examination Centre Allocation Optimization

This project simulates examination centre allocation and compares a baseline administrative assignment with an optimized assignment that minimizes student hardship.

The optimized model uses PuLP when available. If PuLP is not installed, the project falls back to an exact standard-library min-cost-flow solver so the experiment can still run in a bare Python environment.

## Run

```bash
python3 main.py
```

For a faster smoke test:

```bash
python3 main.py --students 120 --skip-sensitivity
```

## Outputs

- `data/students.csv`
- `data/centres.csv`
- `data/preferences.csv`
- `data/distance_matrix.csv`
- `data/hardship_matrix.csv`
- `results/baseline_assignment.csv`
- `results/optimized_assignment.csv`
- `results/baseline_metrics.csv`
- `results/optimized_metrics.csv`
- `results/sensitivity_results.csv`
- `plots/distance_comparison.png`
- `plots/preference_satisfaction.png`
- `plots/hardship_comparison.png`
- `plots/sensitivity_comparison.png`

## Optional Dependencies

```bash
python3 -m pip install -r requirements.txt
```

The current code path does not require these packages to run, but PuLP can be used for the ILP solver path when installed.
