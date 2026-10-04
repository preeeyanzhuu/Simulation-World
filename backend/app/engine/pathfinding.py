import heapq


GRID_SIZE = 30

ROAD_COST = 1
OFFROAD_COST = 3


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step_cost(grid, cell):
    return ROAD_COST if grid[cell[0]][cell[1]]["type"] == "road" else OFFROAD_COST


def get_neighbors(cell, grid, road_closures=None):
    row = cell[0]
    col = cell[1]

    num_rows = len(grid)
    num_cols = len(grid[0]) if num_rows else 0

    candidates = [
        (row + 1, col),
        (row - 1, col),
        (row, col + 1),
        (row, col - 1)
    ]

    valid_neighbors = []

    for n in candidates:
        if 0 <= n[0] < num_rows:
            if 0 <= n[1] < num_cols:
                cell_data = grid[n[0]][n[1]]

                if cell_data["type"] == "building":
                    continue

                if road_closures is not None and cell_data["type"] == "road":
                    road_id = cell_data.get("road_id")
                    if road_id is not None and road_closures.is_closed(road_id):
                        continue

                valid_neighbors.append(n)

    return valid_neighbors


def astar(start, goal, grid, road_closures=None):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for neighbor in get_neighbors(current, grid, road_closures):
            tentative_g = g_score[current] + step_cost(grid, neighbor)

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return None
