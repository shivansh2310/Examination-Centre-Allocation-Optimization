from collections import defaultdict
from heapq import heappop, heappush

from .config import DATA_DIR, RESULTS_DIR
from .hardship_matrix import build_hardship_matrix
from .io_utils import read_csv, write_csv


def allocate_optimized(
    students: list[dict] | None = None,
    centres: list[dict] | None = None,
    hardship_rows: list[dict] | None = None,
    output_path=RESULTS_DIR / "optimized_assignment.csv",
    solver_time_limit: int = 120,
) -> list[dict]:
    students = students if students is not None else read_csv(DATA_DIR / "students.csv")
    centres = centres if centres is not None else read_csv(DATA_DIR / "centres.csv")
    hardship_rows = hardship_rows if hardship_rows is not None else build_hardship_matrix(students, centres)

    if sum(int(centre["capacity"]) for centre in centres) < len(students):
        raise ValueError("Total centre capacity is smaller than the number of students.")

    try:
        return _allocate_with_pulp(students, centres, hardship_rows, output_path, solver_time_limit)
    except ModuleNotFoundError:
        return _allocate_with_min_cost_flow(students, centres, hardship_rows, output_path)


def _allocate_with_pulp(
    students: list[dict],
    centres: list[dict],
    hardship_rows: list[dict],
    output_path,
    solver_time_limit: int,
) -> list[dict]:
    import pulp

    student_ids = [row["student_id"] for row in students]
    centre_ids = [row["centre_id"] for row in centres]
    capacities = {row["centre_id"]: int(row["capacity"]) for row in centres}
    hardship = {
        (row["student_id"], row["centre_id"]): float(row["hardship"])
        for row in hardship_rows
    }

    problem = pulp.LpProblem("exam_centre_allocation", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("assign", (student_ids, centre_ids), cat="Binary")
    problem += pulp.lpSum(hardship[(student_id, centre_id)] * x[student_id][centre_id] for student_id in student_ids for centre_id in centre_ids)

    for student_id in student_ids:
        problem += pulp.lpSum(x[student_id][centre_id] for centre_id in centre_ids) == 1
    for centre_id in centre_ids:
        problem += pulp.lpSum(x[student_id][centre_id] for student_id in student_ids) <= capacities[centre_id]

    status = problem.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit))
    if pulp.LpStatus[status] not in {"Optimal", "Not Solved"}:
        raise RuntimeError(f"PuLP solver failed with status: {pulp.LpStatus[status]}")

    assignments = []
    for student_id in student_ids:
        assigned = max(centre_ids, key=lambda centre_id: pulp.value(x[student_id][centre_id]) or 0)
        assignments.append({"student_id": student_id, "centre_id": assigned})
    write_csv(output_path, assignments)
    return assignments


class _Edge:
    def __init__(self, to: int, rev: int, capacity: int, cost: float, label=None):
        self.to = to
        self.rev = rev
        self.capacity = capacity
        self.cost = cost
        self.label = label


def _add_edge(graph: list[list[_Edge]], src: int, dst: int, capacity: int, cost: float, label=None) -> None:
    forward = _Edge(dst, len(graph[dst]), capacity, cost, label)
    backward = _Edge(src, len(graph[src]), 0, -cost, None)
    graph[src].append(forward)
    graph[dst].append(backward)


def _allocate_with_min_cost_flow(
    students: list[dict],
    centres: list[dict],
    hardship_rows: list[dict],
    output_path,
) -> list[dict]:
    student_ids = [row["student_id"] for row in students]
    centre_ids = [row["centre_id"] for row in centres]
    student_node = {student_id: index + 1 for index, student_id in enumerate(student_ids)}
    centre_node = {
        centre_id: len(student_ids) + index + 1 for index, centre_id in enumerate(centre_ids)
    }
    source = 0
    sink = len(student_ids) + len(centre_ids) + 1
    graph: list[list[_Edge]] = [[] for _ in range(sink + 1)]

    for student_id in student_ids:
        _add_edge(graph, source, student_node[student_id], 1, 0)
    for centre in centres:
        _add_edge(graph, centre_node[centre["centre_id"]], sink, int(centre["capacity"]), 0)
    for row in hardship_rows:
        _add_edge(
            graph,
            student_node[row["student_id"]],
            centre_node[row["centre_id"]],
            1,
            float(row["hardship"]),
            label=(row["student_id"], row["centre_id"]),
        )

    potentials = [0.0] * len(graph)
    flow = 0
    required_flow = len(student_ids)
    while flow < required_flow:
        dist = [float("inf")] * len(graph)
        previous: list[tuple[int, int] | None] = [None] * len(graph)
        dist[source] = 0.0
        heap = [(0.0, source)]
        while heap:
            current_dist, node = heappop(heap)
            if current_dist > dist[node]:
                continue
            for edge_index, edge in enumerate(graph[node]):
                if edge.capacity <= 0:
                    continue
                next_dist = current_dist + edge.cost + potentials[node] - potentials[edge.to]
                if next_dist < dist[edge.to]:
                    dist[edge.to] = next_dist
                    previous[edge.to] = (node, edge_index)
                    heappush(heap, (next_dist, edge.to))

        if previous[sink] is None:
            raise RuntimeError("No feasible optimized allocation found.")

        for node, node_dist in enumerate(dist):
            if node_dist < float("inf"):
                potentials[node] += node_dist

        increment = required_flow - flow
        node = sink
        while node != source:
            prev_node, edge_index = previous[node]
            increment = min(increment, graph[prev_node][edge_index].capacity)
            node = prev_node

        node = sink
        while node != source:
            prev_node, edge_index = previous[node]
            edge = graph[prev_node][edge_index]
            edge.capacity -= increment
            graph[node][edge.rev].capacity += increment
            node = prev_node
        flow += increment

    assignments = []
    for student_id in student_ids:
        node = student_node[student_id]
        for edge in graph[node]:
            if edge.label and graph[edge.to][edge.rev].capacity > 0:
                assignments.append({"student_id": student_id, "centre_id": edge.label[1]})
                break

    if len(assignments) != len(students):
        counts = defaultdict(int)
        for assignment in assignments:
            counts[assignment["student_id"]] += 1
        missing = [student_id for student_id in student_ids if counts[student_id] != 1]
        raise RuntimeError(f"Invalid optimized assignment. Missing/duplicate students: {missing[:5]}")

    write_csv(output_path, assignments)
    return assignments
