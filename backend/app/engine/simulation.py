import asyncio
import itertools
import random
from collections import Counter, defaultdict, deque

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.engine.pathfinding import astar
from app.models.building import Hospital, School, Office, Park, Restaurant, Mall, House
from app.models.citizen import (
    Doctor, Teacher, Shopkeeper, OfficeWorker, Student, LearningAgent, Citizen,
)
from app.models.road import Road
from app.ai.actions import ACTIONS
from app.ai.brain import think
from app.ai.learning import (
    build_event_flags,
    calculate_arrival_reward,
    calculate_tick_penalty,
    get_state,
)
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

WAGE = 20
ALLOWANCE_FALLBACK = 15
RESTAURANT_COST = 10
MALL_COST = 10   
HUNGER_RELIEF = 40
ENERGY_RELIEF = 40
HAPPINESS_BOOST = 20

Q_SAVE_INTERVAL = 500

ACTION_BUILDING = {
    "go_restaurant": "restaurant",
    "go_mall": "mall",
    "go_park": "park",
    "go_school": "school",
}


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


def initialize_city_state(state, force=False):
    if state.citizens and not force:
        return
    state.citizens = []
    state.buildings = []
    state.building_entrances = {}
    state.entrance_by_building = {}
    state.roads = []
    state.intersections = set()
    state.reward_history = []
    Citizen.reset_id_counter()

    from app.world.city import create_grid
    state.grid = create_grid()
    grid = state.grid

    north_road = Road(
        "north_road",
        cells=[(2, c) for c in range(2, 28)]
    )
    north_west_road = Road(
        "north_west_road",
        cells=[(r, 2) for r in range(2, 8)]
    )
    north_center_road = Road(
        "north_center_road",
        cells=[(r, 16) for r in range(2, 8)]
    )
    north_east_inner_road = Road(
        "north_east_inner_road",
        cells=[(r, 21) for r in range(2, 8)]
    )
    north_east_outer_road = Road(
        "north_east_outer_road",
        cells=[(r, 28) for r in range(2, 8)]
    )
    upper_middle_road = Road(
        "upper_middle_road",
        cells=[(7, c) for c in range(2, 29)]
    )
    left_middle_road = Road(
        "left_middle_road",
        cells=[(r, 4) for r in range(7, 21)]
    )
    center_upper_road = Road(
        "center_upper_road",
        cells=[(r, 16) for r in range(7, 14)]
    )
    right_middle_road = Road(
        "right_middle_road",
        cells=[(r, 21) for r in range(7, 21)]
    )
    middle_road = Road(
        "middle_road",
        cells=[(13, c) for c in range(4, 29)]
    )
    lower_road = Road(
        "lower_road",
        cells=[(20, c) for c in range(4, 29)]
    )
    lower_center_road = Road(
        "lower_center_road",
        cells=[(r, 11) for r in range(20, 29)]
    )
    south_road = Road(
        "south_road",
        cells=[(28, c) for c in range(11, 29)]
    )
    south_east_road = Road(
        "south_east_road",
        cells=[(r, 28) for r in range(8, 29)]
    )

    all_roads = (
        north_road, north_west_road, north_center_road, north_east_inner_road,
        north_east_outer_road, upper_middle_road, left_middle_road,
        center_upper_road, right_middle_road, middle_road, lower_road,
        lower_center_road, south_road, south_east_road,
    )
    for road in all_roads:
        road.place_on_grid(grid)

    state.roads = list(all_roads)
    cell_counts = Counter(cell for road in all_roads for cell in road.cells)
    state.intersections = {cell for cell, n in cell_counts.items() if n > 1}

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
        [(House, 4)] * 15
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
            (r, c) for r in range(len(grid)) for c in range(len(grid[0]))
            if grid[r][c]["type"] != "building"
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

    houses = buildings_by_type["house"]
    state.buildings = buildings
    state.entrance_by_building = {id(b): _entrance_cell(b) for b in buildings}
    state.building_entrances = {
        btype: [_entrance_cell(b) for b in blds]
        for btype, blds in buildings_by_type.items()
    }

    citizens = _generate_population()

    house_slots = [h for h in houses for _ in range(h.capacity)]
    if len(house_slots) < len(citizens):
        raise RuntimeError(f"Only {len(house_slots)} beds for {len(citizens)} citizens - add more houses.")

    for citizen, house in zip(citizens, house_slots):
        citizen.y, citizen.x = house.location
        citizen.home_entrance = _entrance_cell(house)
        citizen.set_path([])
        citizen.current_action = "idle"
        state.add_citizen(citizen)
    state._layout_version = getattr(state, "_layout_version", 0) + 1
    state._layout_sent_to = set()


def action_building_type(citizen, action):
    if action == "go_work":
        return getattr(citizen, "workplace", None)
    return ACTION_BUILDING.get(action)


def is_action_available(state, citizen, action):
    if action in ("idle", "go_home"):
        return True
    btype = action_building_type(citizen, action)
    if btype is None:
        return False
    hour = state.clock.hour
    return any(b.is_open(hour) for b in state.buildings if b.building_type == btype)


def resolve_goal(state, citizen, action):
    if action == "go_home":
        return citizen.home_entrance

    btype = action_building_type(citizen, action)
    entrances = state.building_entrances.get(btype) if btype else None
    if not entrances:
        return None
    cy, cx = citizen.y, citizen.x
    return min(entrances, key=lambda e: abs(e[0] - cy) + abs(e[1] - cx))


def has_room(state, citizen, action):
    btype = action_building_type(citizen, action)
    if btype is None:                 
        return True
    cell = (citizen.y, citizen.x)
    hour = state.clock.hour
    capacity = sum(
        b.capacity for b in state.buildings
        if b.building_type == btype and b.is_open(hour)
        and state.entrance_by_building.get(id(b)) == cell
    )
    if capacity == 0:
        return False
    inside = sum(
        1 for o in state.citizens
        if o is not citizen and o.is_alive and (o.y, o.x) == cell
        and o.current_action == action and o.arrived_effect_done
    )
    return inside < capacity


def apply_arrival_effect(state, citizen, action):
    if action == "go_home":
        citizen.energy = min(100, citizen.energy + ENERGY_RELIEF)
        return True
    elif action == "go_restaurant" and citizen.money >= RESTAURANT_COST:
        citizen.money -= RESTAURANT_COST
        citizen.hunger = max(0, citizen.hunger - HUNGER_RELIEF)
        return True
    elif action == "go_mall":
        if citizen.money >= MALL_COST:
            citizen.money -= MALL_COST
            citizen.happiness = min(100, citizen.happiness + HAPPINESS_BOOST)
            return True
        return False
    elif action == "go_park":
        citizen.happiness = min(100, citizen.happiness + HAPPINESS_BOOST)
        return True
    elif action == "go_work" and citizen.occupation != "student":
        wage = WAGE
        if state.tax_state.active:
            wage *= state.tax_state.multiplier
        citizen.money += wage
        return True
    elif action == "go_school" and citizen.occupation == "student":
        if hasattr(citizen, "receive_allowance"):
            citizen.receive_allowance()
        else:
            citizen.money += ALLOWANCE_FALLBACK
        return True
    return False


def _try_arrival(state, citizen, time_of_day=None, events=None):
    action = citizen.current_action
    if action in (None, "idle") or not citizen.path or citizen.arrived_effect_done:
        return
    if citizen.path_index != len(citizen.path) - 1:
        return
    if not (is_action_available(state, citizen, action) and has_room(state, citizen, action)):
        return

    before = {
        "energy": citizen.energy,
        "hunger": citizen.hunger,
        "happiness": citizen.happiness,
        "money": citizen.money,
    }
    apply_arrival_effect(state, citizen, action)
    citizen.arrived_effect_done = True

    reward = calculate_arrival_reward(
        citizen, action, tax_state=state.tax_state, before=before
    )
    citizen.last_reward = reward
    learner = getattr(citizen, "learner", None)
    if learner is not None and learner._pending is not None:
        next_state = get_state(
            citizen,
            time_of_day or state.clock.get_time_period(),
            events=events or build_event_flags(weather=state.weather, tax_state=state.tax_state),
        )
        learner.complete_action(reward, next_state)
        memory = getattr(citizen, "memory", None)
        if memory is not None and memory.history:
            state_m, action_m, _ = memory.history[-1]
            memory.history[-1] = (state_m, action_m, reward)


def _replan_on_closure_change(state):
    closed = tuple(sorted(state.road_closures.closed_road_ids()))
    if closed == state.__dict__.get("_closed_snapshot", ()):
        return
    state._closed_snapshot = closed
    for c in state.citizens:
        if c.is_alive and c.path and c.path_index < len(c.path) - 1:
            new_path = astar((c.y, c.x), c.path[-1], state.grid, state.road_closures)
            if new_path:
                c.set_path(new_path)

DECISION_INTERVAL = 8


def _is_mid_trip(state, citizen):
    if citizen.current_action in ("idle", None):
        return False
    if not citizen.path or citizen.path_index >= len(citizen.path) - 1:
        return False
    if not is_action_available(state, citizen, citizen.current_action):
        return False
    return True


def _should_redecide(state, citizen):
    if _is_mid_trip(state, citizen):
        return False
    if citizen.occupation == "learning_agent":
        last = getattr(citizen, "_last_decision_tick", -999)
        just_arrived = citizen.arrived_effect_done and citizen.path and (
            citizen.path_index >= len(citizen.path) - 1
        )
        if just_arrived:
            return True
        return (state.clock.tick - last) >= DECISION_INTERVAL
    return True


def step_simulation(state, action_fn=None):
    state.update()
    _replan_on_closure_change(state)

    time_of_day = state.clock.get_time_period()
    events = build_event_flags(weather=state.weather, tax_state=state.tax_state)
    raining = state.weather.is_raining()
    rewards = {}

    for c in state.citizens:
        if not c.is_alive:
            continue

        c.advance(can_move=not (raining and state.clock.tick % 2 == 0))
        if not c.is_alive:    
            continue

        _try_arrival(state, c, time_of_day=time_of_day, events=events)

        if not _should_redecide(state, c):
            action = c.current_action or "idle"
        elif action_fn is None:
            allowed = [a for a in ACTIONS if is_action_available(state, c, a)]
            action = think(
                c,
                learner=getattr(c, "learner", None),
                memory=getattr(c, "memory", None),
                tax_state=state.tax_state,
                time_of_day=time_of_day,
                events=events,
                allowed_actions=allowed,
            )
            c._last_decision_tick = state.clock.tick
        else:
            action = action_fn(c, time_of_day, events)
            c._last_decision_tick = state.clock.tick

        if not is_action_available(state, c, action):
            action = "idle"
        tick_r = calculate_tick_penalty(c)
        if not c.arrived_effect_done or c.current_action in (None, "idle"):
            if c.last_reward == 0.0 or c.current_action in (None, "idle"):
                c.last_reward = tick_r
        rewards[c.id] = c.last_reward

        if action == "idle":
            c.current_action = "idle"
            if c.path:
                c.set_path([])
        else:
            if action != c.current_action or not c.path:
                goal = resolve_goal(state, c, action)
                if goal is not None:
                    c.set_path(astar((c.y, c.x), goal, state.grid, state.road_closures))
                c.current_action = action

            _try_arrival(state, c, time_of_day=time_of_day, events=events)
    if state.clock.tick > 0 and state.clock.tick % Q_SAVE_INTERVAL == 0:
        _save_all_learners(state)

    return rewards


def _save_all_learners(state):
    merged = None
    for c in state.citizens:
        if c.occupation == "learning_agent" and hasattr(c, "learner"):
            if merged is None:
                merged = c.learner
            else:
                for key, q in c.learner.q_table.items():
                    prev = merged.q_table.get(key, 0.0)
                    if abs(q) >= abs(prev):
                        merged.q_table[key] = q
    if merged is not None:
        merged.save_q_table(LearningAgent.DEFAULT_Q_PATH)


def build_frame(state, client_id=None, full_layout=False):
    frame = {
        "type": "update",
        "grid_size": len(state.grid),
        "running": sim_control.running,
        "agents": [c.to_dict() for c in state.citizens],
        "hour": state.clock.hour,
        "day": state.clock.day,
        "weather": state.weather.current_state,
        "timePeriod": state.clock.get_time_period(),
        "taxActive": state.tax_state.active,
        "roadClosureActive": bool(state.road_closures.closed_road_ids()),
        "closedRoadIds": state.road_closures.closed_road_ids(),
        "streetLightsOn": state.street_light.is_on,
        "rewardHistory": state.reward_history,
        "layoutVersion": getattr(state, "_layout_version", 0),
    }

    if full_layout:
        frame["type"] = "layout"
        frame["roads"] = [r.to_dict() for r in state.roads]
        frame["intersections"] = sorted(state.intersections)
        frame["buildings"] = [b.to_dict() for b in state.buildings]

    return frame
_clients = set()      
_sim_task = None
_layout_ack = {}      


async def _simulation_loop():
    initialize_city_state(city_state)
    sim_control.start()

    while True:
        try:
            if sim_control.running:
                rewards = step_simulation(city_state)

                learner_rewards = [
                    r for c in city_state.citizens
                    if c.occupation == "learning_agent"
                    and (r := rewards.get(c.id)) is not None
                ]
                avg_reward = (
                    sum(learner_rewards) / len(learner_rewards)
                    if learner_rewards else 0.0
                )
                city_state.reward_history.append(avg_reward)
                if len(city_state.reward_history) > 60:
                    city_state.reward_history.pop(0)

            layout_version = getattr(city_state, "_layout_version", 0)
            dead = []
            for ws in list(_clients):
                try:
                    client_key = id(ws)
                    needs_layout = _layout_ack.get(client_key, -1) < layout_version
                    frame = build_frame(city_state, full_layout=needs_layout)
                    await ws.send_json(frame)
                    if needs_layout:
                        _layout_ack[client_key] = layout_version
                except Exception:
                    dead.append(ws)

            for ws in dead:
                _clients.discard(ws)
                _layout_ack.pop(id(ws), None)

            await asyncio.sleep(0.3)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            print(f"[sim loop] error: {exc}")
            await asyncio.sleep(0.5)


def ensure_simulation_running():
    global _sim_task
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    if _sim_task is None or _sim_task.done():
        _sim_task = loop.create_task(_simulation_loop())


async def register_client(websocket: WebSocket):
    await websocket.accept()
    _clients.add(websocket)
    ensure_simulation_running()
    _layout_ack[id(websocket)] = -1
    try:
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        _clients.discard(websocket)
        _layout_ack.pop(id(websocket), None)
async def run_simulation(websocket: WebSocket):
    await register_client(websocket)
