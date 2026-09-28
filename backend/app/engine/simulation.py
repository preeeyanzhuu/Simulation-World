import asyncio
import itertools
import random
from collections import defaultdict, deque

from fastapi import WebSocket

from app.engine.pathfinding import astar
from app.models.building import Hospital, School, Office, Park, Restaurant, Mall, House
from app.models.citizen import Doctor, Teacher, Shopkeeper, OfficeWorker, Student, LearningAgent
from app.models.road import Road
from app.ai.brain import think
from app.ai.learning import build_event_flags, calculate_reward
from app.world.state import city_state
from app.api.simulation import sim_control

GRID_SIZE = 30
RULE_BASED_COUNTS = [
    (Doctor, 8),
    (Teacher, 8),
    (Student, 12),
    (Shopkeeper, 8),
    (OfficeWorker, 12),
]
LEARNING_AGENT_COUNT = 10
AGE_RANGES = {
    Doctor: (28, 60),
    Teacher: (24, 55),
    Student: (6, 18),
    Shopkeeper: (20, 55),
    OfficeWorker: (22, 50),
    LearningAgent: (20, 40),
}

NAME_POOL = [
    "Aarav", "Priya", "Rohan", "Ananya", "Kabir", "Meera", "Ishaan", "Devika",
    "Farhan", "Kiran", "Lakshmi", "Manav", "Nisha", "Omkar", "Pooja", "Rahul",
    "Sana", "Tara", "Uday", "Vikram", "Yash", "Zara", "Arjun", "Bhavna",
    "Chetan", "Divya", "Esha", "Gaurav", "Harini", "Imran",
]


def _generate_name(index):
    base = NAME_POOL[index % len(NAME_POOL)]
    wrap = index // len(NAME_POOL)
    return base if wrap == 0 else f"{base} {wrap + 1}"


def _randomize_starting_stats(citizen, rng):
    citizen.energy = rng.randint(55, 100)
    citizen.hunger = rng.randint(0, 45)
    citizen.money = rng.randint(20, 80)


def _generate_population():
    rng = random.Random(42)
    citizens = []
    index = 0

    for cls, count in RULE_BASED_COUNTS:
        lo, hi = AGE_RANGES[cls]
        for _ in range(count):
            citizen = cls(name=_generate_name(index), age=rng.randint(lo, hi))
            _randomize_starting_stats(citizen, rng)
            citizens.append(citizen)
            index += 1

    lo, hi = AGE_RANGES[LearningAgent]
    for _ in range(LEARNING_AGENT_COUNT):
        citizen = LearningAgent(name=_generate_name(index), age=rng.randint(lo, hi))
        _randomize_starting_stats(citizen, rng)
        citizens.append(citizen)
        index += 1

    return citizens


def initialize_city_state(state):
    if state.citizens:
        return

    grid = state.grid
    # North horizontal road
    north_road = Road(
        "north_road",
        cells=[(2, c) for c in range(2, 28)]
    )

    # North-west vertical road
    north_west_road = Road(
        "north_west_road",
        cells=[(r, 2) for r in range(2, 8)]
    )

    # North-center vertical road
    north_center_road = Road(
        "north_center_road",
        cells=[(r, 16) for r in range(2, 8)]
    )

    # North-east inner vertical road
    north_east_inner_road = Road(
        "north_east_inner_road",
        cells=[(r, 23) for r in range(2, 8)]
    )

    # North-east outer vertical road
    north_east_outer_road = Road(
        "north_east_outer_road",
        cells=[(r, 27) for r in range(2, 8)]
    )

    # Upper-middle horizontal road
    upper_middle_road = Road(
        "upper_middle_road",
        cells=[(7, c) for c in range(2, 28)]
    )

    # Left-middle vertical road
    left_middle_road = Road(
        "left_middle_road",
        cells=[(r, 4) for r in range(7, 27)]
    )

    # Center-upper vertical road
    center_upper_road = Road(
        "center_upper_road",
        cells=[(r, 10) for r in range(7, 14)]
    )

    # Right-middle vertical road
    right_middle_road = Road(
        "right_middle_road",
        cells=[(r, 21) for r in range(7, 21)]
    )

    # Middle horizontal road
    middle_road = Road(
        "middle_road",
        cells=[(13, c) for c in range(4, 29)]
    )

    # Lower horizontal road
    lower_road = Road(
        "lower_road",
        cells=[(20, c) for c in range(4, 29)]
    )

    # Lower-left/center vertical road
    lower_center_road = Road(
        "lower_center_road",
        cells=[(r, 11) for r in range(20, 29)]
    )

    # Bottom horizontal road
    south_road = Road(
        "south_road",
        cells=[(28, c) for c in range(11, 29)]
    )

    # Right outer vertical road
    south_east_road = Road(
        "south_east_road",
        cells=[(r, 28) for r in range(8, 29)]
    )
    

    
    for road in (north_road, north_west_road, north_center_road, north_east_inner_road, north_east_outer_road, upper_middle_road, left_middle_road, center_upper_road, right_middle_road,middle_road, lower_road,lower_center_road,south_road,south_east_road):
        road.place_on_grid(grid)

    def _entrance_cell(building):
        for r, c in building.get_occupied_cells():
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc]["type"] != "building":
                    return (nr, nc)
        return building.location

    def _reachable_cells(grid, start):
        rows, cols = len(grid), len(grid[0])
        seen = {start}
        queue = deque([start])
        while queue:
            r, c = queue.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and grid[nr][nc]["type"] != "building":
                    seen.add((nr, nc))
                    queue.append((nr, nc))
        return seen

    def _random_footprint(grid, w, h, rng, margin=1, max_attempts=3000):
        rows, cols = len(grid), len(grid[0])
        for _ in range(max_attempts):
            r = rng.randint(margin, rows - h - margin)
            c = rng.randint(margin, cols - w - margin)
            if all(grid[rr][cc]["type"] == "empty" for rr in range(r, r + h) for cc in range(c, c + w)):
                return (r, c)
        return None

    def _place_buildings_scattered(grid, specs, rng):
        placed = []
        for cls, capacity in specs:
            probe = cls((0, 0), capacity)
            w, h = probe.width, probe.height
            loc = _random_footprint(grid, w, h, rng)
            if loc is None:
                raise RuntimeError(f"No space left to scatter a {cls.__name__} ({w}x{h}).")
            b = cls(loc, capacity)
            for r, c in b.get_occupied_cells():
                grid[r][c] = {"type": "building", "name": b.to_dict()}
            placed.append(b)
        return placed

    def _clear_buildings(grid):
        for row in grid:
            for cell in row:
                if cell["type"] == "building":
                    cell.clear()
                    cell["type"] = "empty"

    building_specs = (
        [(House, 4)] * 12
        + [(School, 20)] * 2
        + [(Office, 50)] * 2
        + [(Mall, 10)] * 3
        + [(Restaurant, 20)] * 2
        + [(Hospital, 10)]
        + [(Park, 30)] * 2
    )

    layout_rng = random.Random(7)
    buildings = None
    for _ in range(20): 
        _clear_buildings(grid)
        specs = list(building_specs)
        layout_rng.shuffle(specs)
        candidate = _place_buildings_scattered(grid, specs, layout_rng)

        start_cell = next(
            (r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c]["type"] != "building"
        )
        reachable = _reachable_cells(grid, start_cell)
        if all(_entrance_cell(b) in reachable for b in candidate):
            buildings = candidate
            break
    if buildings is None:
        raise RuntimeError("Could not find a fully-reachable random building layout after 20 attempts.")

    buildings_by_type = defaultdict(list)
    for b in buildings:
        buildings_by_type[b.building_type].append(b)

    house_cycle = itertools.cycle(buildings_by_type["house"])
    workplace_cycles = {
        btype: itertools.cycle([_entrance_cell(b) for b in blds])
        for btype, blds in buildings_by_type.items()
        if btype != "house"
    }
    state.buildings = buildings
    state.building_entrances = {
        btype: [_entrance_cell(b) for b in blds] for btype, blds in buildings_by_type.items()
    }

    citizens = _generate_population()

    for citizen in citizens:
        house = next(house_cycle)
        start = house.location
        workplace_type = getattr(citizen, "workplace", None)
        goal = next(workplace_cycles[workplace_type]) if workplace_type in workplace_cycles else start

        citizen.y, citizen.x = start
        citizen.home_entrance = _entrance_cell(house)
        path = astar(start, goal, grid, state.road_closures)
        citizen.set_path(path)
        citizen.current_action = "go_work" if workplace_type else "idle"
        state.add_citizen(citizen)

WAGE = 20
ALLOWANCE_FALLBACK = 15
RESTAURANT_COST = 10
HUNGER_RELIEF = 40
ENERGY_RELIEF = 40
HAPPINESS_BOOST = 20


def resolve_goal(state, citizen, action):
    """Map a decide()/QLearner action to a walkable target cell."""
    if action == "go_home":
        return citizen.home_entrance

    btype = citizen.workplace if action in ("go_work", "go_school") else {
        "go_restaurant": "restaurant",
        "go_mall": "mall",
    }.get(action)

    entrances = state.building_entrances.get(btype) if btype else None
    if not entrances:
        return None
    cy, cx = citizen.y, citizen.x
    return min(entrances, key=lambda e: abs(e[0] - cy) + abs(e[1] - cx))


def apply_arrival_effect(state, citizen, action):
    if action == "go_home":
        citizen.energy = min(100, citizen.energy + ENERGY_RELIEF)
    elif action == "go_restaurant" and citizen.money >= RESTAURANT_COST:
        citizen.money -= RESTAURANT_COST
        citizen.hunger = max(0, citizen.hunger - HUNGER_RELIEF)
    elif action == "go_mall":
        citizen.happiness = min(100, citizen.happiness + HAPPINESS_BOOST)
    elif action == "go_work":
        wage = WAGE
        if state.tax_state.active:
            wage *= state.tax_state.multiplier
        citizen.money += wage
    elif action == "go_school" and citizen.occupation == "student":
        if hasattr(citizen, "receive_allowance"):
            citizen.receive_allowance()
        else:
            citizen.money += ALLOWANCE_FALLBACK


def step_simulation(state, action_fn=None):
    state.update()

    time_of_day = state.clock.get_time_period()
    events = build_event_flags(weather=state.weather, tax_state=state.tax_state)
    rewards = {}

    for c in state.citizens:
        c.advance()

        if action_fn is None:
            action = think(
                c,
                learner=getattr(c, "learner", None),
                memory=getattr(c, "memory", None),
                tax_state=state.tax_state,
                time_of_day=time_of_day,
                events=events,
            )
        else:
            action = action_fn(c, time_of_day, events)
        rewards[c.id] = calculate_reward(c, action, tax_state=state.tax_state)

        if action == "idle":
            c.current_action = "idle"
        else:
            if action != c.current_action or not c.path:
                goal = resolve_goal(state, c, action)
                if goal is not None:
                    c.set_path(astar((c.y, c.x), goal, state.grid, state.road_closures))
                c.current_action = action

            arrived = c.path and c.path_index == len(c.path) - 1
            if arrived and not c.arrived_effect_done:
                apply_arrival_effect(state, c, action)
                c.arrived_effect_done = True

    return rewards


async def run_simulation(websocket: WebSocket):
    initialize_city_state(city_state)
    sim_control.start()

    while True:
        if sim_control.running:
            rewards = step_simulation(city_state)

            learner_rewards = [
                r for c in city_state.citizens
                if c.occupation == "learning_agent" and (r := rewards.get(c.id)) is not None
            ]
            avg_reward = sum(learner_rewards) / len(learner_rewards) if learner_rewards else 0.0
            city_state.reward_history.append(avg_reward)
            if len(city_state.reward_history) > 60:
                city_state.reward_history.pop(0)

        state = {
            "grid_size": len(city_state.grid),
            "grid": city_state.grid,
            "agents": [c.to_dict() for c in city_state.citizens],
            "buildings": [b.to_dict() for b in city_state.buildings],
            "hour": city_state.clock.hour,
            "day": city_state.clock.day,
            "weather": city_state.weather.current_state,
            "timePeriod": city_state.clock.get_time_period(),
            "taxActive": city_state.tax_state.active,
            "roadClosureActive": bool(city_state.road_closures.closed_road_ids()),
            "closedRoadIds": city_state.road_closures.closed_road_ids(),
            "rewardHistory": city_state.reward_history,
        }

        await websocket.send_json(state)
        await asyncio.sleep(0.3)
