# Examination Centre Allocation Optimization Research Project

## Project Overview

This project aims to investigate whether examination centre allocation can be improved using mathematical optimization techniques.

Current examination allocation systems often assign students to distant examination centres despite the existence of closer or more accessible alternatives. This may increase travel burden, reduce preference satisfaction, increase financial cost, and negatively impact examination performance.

The goal of this research is to model examination centre allocation as an optimization problem and compare optimized allocations against a baseline administrative allocation model.

The project is intended as an experimental applied mathematics and operations research study using synthetic data.

---

# Research Objective

Develop a simulation framework that:

1. Generates a synthetic examination environment.
2. Generates students and examination centres.
3. Generates student examination city preferences.
4. Computes assignment hardship.
5. Produces a baseline allocation.
6. Produces an optimized allocation using Integer Linear Programming.
7. Compares both systems using quantitative metrics.

---

# Mathematical Model

## Sets

Students:

[
S={S_1,S_2,\dots,S_n}
]

Examination Centres:

[
C={C_1,C_2,\dots,C_m}
]

---

## Decision Variable

[
x_{ij}
======

\begin{cases}
1 & \text{if student } i \text{ assigned to centre } j\
0 & \text{otherwise}
\end{cases}
]

---

## Hardship Function

The hardship score for assigning student (i) to centre (j) is:

[
H_{ij}
======

\alpha D_{ij}
+
\beta A_j^{pen}
+
\lambda P_{ij}
]

where:

* (D_{ij}) = distance between student and centre
* (A_j^{pen}) = accessibility penalty
* (P_{ij}) = preference penalty

---

## Objective Function

Minimize total hardship:

[
\min Z
======

\sum_i
\sum_j
H_{ij}x_{ij}
]

---

## Constraints

### Assignment Constraint

Every student must receive exactly one centre:

[
\sum_j x_{ij}=1
]

### Capacity Constraint

Centre capacity must not be exceeded:

[
\sum_i x_{ij}
\le
C_j^{max}
]

### Binary Constraint

[
x_{ij}\in{0,1}
]

---

# Prototype Environment

## Scale

Prototype Version:

* 2,000 students
* 20 districts
* 20 examination centres

Future Scale:

* 10,000+ students
* 50+ centres

---

# District Structure

Synthetic districts:

```python
districts = [
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
    "Metro"
]
```

---

# Geography Generation

Use clustered coordinates.

Example:

North districts:

```text
y ≈ 800
```

South districts:

```text
y ≈ 200
```

East districts:

```text
x ≈ 800
```

West districts:

```text
x ≈ 200
```

Metro:

```text
(500,500)
```

Add small random noise.

---

# Student Generation

Each student should contain:

```python
student_id
district
x
y
gender
```

Gender:

```python
["M","F"]
```

Home coordinates should be generated around the student's district centroid.

---

# Centre Generation

Each centre should contain:

```python
centre_id
district
x
y
capacity
transport_quality
food_availability
accommodation_availability
```

Capacity:

```python
200 - 500
```

---

# Accessibility Model

Generate:

```python
transport_quality
food_availability
accommodation_availability
```

Range:

```python
1 - 10
```

Accessibility Score:

[
A_j
===

\frac{
TQ_j
+
FA_j
+
AA_j
}{3}
]

Accessibility Penalty:

[
A_j^{pen}
=========

10-A_j
]

---

# Preference Generation

Each student selects:

```python
pref_1
pref_2
pref_3
```

Preferences should be generated using a distance-based probability model.

Closer districts should have higher probability of being selected.

Do not assign preferences uniformly.

---

# Distance Matrix

Compute:

[
D_{ij}
======

\sqrt{
(x_i-x_j)^2
+
(y_i-y_j)^2
}
]

for every student-centre pair.

Store as:

```python
distance_matrix
```

---

# Preference Penalty

Use:

| Assignment          | Penalty |
| ------------------- | ------- |
| First Preference    | 0       |
| Second Preference   | 5       |
| Third Preference    | 10      |
| Outside Preferences | 50      |

---

# Hardship Matrix

Generate:

```python
hardship_matrix
```

using:

[
H_{ij}
======

\alpha D_{ij}
+
\beta A_j^{pen}
+
\lambda P_{ij}
]

Default weights:

```python
alpha = 0.60
beta = 0.20
lambda_ = 0.20
```

---

# Baseline Allocation

Implement a simple administrative allocation model.

Requirements:

* Respect centre capacities.
* Ignore hardship.
* Ignore preferences.
* Ignore accessibility.

Can be random or first-fit assignment.

Output:

```python
baseline_assignment
```

---

# Optimized Allocation

Use:

```python
PuLP
```

Implement Integer Linear Programming.

Output:

```python
optimized_assignment
```

---

# Metrics

Calculate:

## Average Distance

```python
avg_distance
```

---

## Maximum Distance

```python
max_distance
```

---

## Preference Satisfaction Rate

Percentage receiving:

* 1st preference
* 2nd preference
* 3rd preference
* Outside preferences

---

## Average Hardship

```python
avg_hardship
```

---

## Centre Utilization

```python
utilization_rate
```

---

# Sensitivity Analysis

Implement multiple scenarios.

## Distance Focused

```python
alpha = 0.80
beta = 0.10
lambda_ = 0.10
```

## Preference Focused

```python
alpha = 0.40
beta = 0.10
lambda_ = 0.50
```

## Accessibility Focused

```python
alpha = 0.40
beta = 0.50
lambda_ = 0.10
```

## Balanced

```python
alpha = 0.60
beta = 0.20
lambda_ = 0.20
```

---

# Required Output Files

```text
project/
│
├── data/
│   ├── students.csv
│   ├── centres.csv
│   ├── preferences.csv
│
├── src/
│   ├── generate_data.py
│   ├── distance_matrix.py
│   ├── hardship_matrix.py
│   ├── baseline_allocator.py
│   ├── optimizer.py
│   ├── metrics.py
│   ├── sensitivity.py
│
├── results/
│   ├── baseline_metrics.csv
│   ├── optimized_metrics.csv
│   ├── sensitivity_results.csv
│
├── plots/
│   ├── distance_comparison.png
│   ├── preference_satisfaction.png
│   ├── hardship_comparison.png
│
└── main.py
```

---

# Success Criteria

The optimized allocation should outperform the baseline allocation in at least:

* Average travel distance
* Preference satisfaction
* Average hardship

while respecting all assignment and capacity constraints.

The code should be reproducible, modular, and easily scalable from 2,000 students to larger populations.
