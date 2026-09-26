import asyncio

from fastapi import WebSocket

from app.engine.pathfinding import astar
from app.models.building import Hospital, School, Office, Park, Restaurant, Mall, House
from app.models.citizen import Citizen, Doctor, Teacher, Shopkeeper, OfficeWorker, Student
from app.models.road import Road
from app.ai.brain import think
from app.ai.learning import build_event_flags
from app.world.state import city_state
from app.api.simulation import sim_control

GRID_SIZE = 30


def _pack_region(grid, buildings, row_start, row_end, col_start, col_end, pitch):
    placed = []
    row, col = row_start, col_start
    for cls, capacity in buildings:
        probe = cls((0, 0), capacity)
        w, h = probe.width, probe.height

        if col + w > col_end:
            col = col_start
            row += pitch
        if row + h > row_end:
            raise ValueError(f"ran out of space placing {cls.__name__} in region")

        b = cls((row, col), capacity)
        for r, c in b.get_occupied_cells():
            grid[r][c] = {"type": "building", "name": b.to_dict()}
        placed.append(b)
        col += pitch
    return placed


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

    TL = (0, 1, 0, 15)
    TM = (0, 5, 17, 22)
    TR = (0, 5, 16, 25)
    BL = (21, 27, 5, 9)
    BM = (21, 27, 12, 20)
    BR = (21, 27, 22, 27)

    buildings = []
    buildings += _pack_region(grid, [(House, 4)] * 6, *TL, pitch=2)
    buildings += _pack_region(grid, [(House, 4)] * 6, *BL, pitch=2)
    buildings += _pack_region(grid, [(School, 20), (School, 20), (Office, 50)], *TM, pitch=2)
    buildings += _pack_region(grid, [(Office, 50), (Mall, 10), (Mall, 10), (Restaurant, 20)], *TR, pitch=2)
    buildings += _pack_region(grid, [(Hospital, 10), (Park, 30)], *BM, pitch=4)
    buildings += _pack_region(grid, [(Park, 30), (Mall, 10), (Restaurant, 20)], *BR, pitch=4)

    house_starts = [b.location for b in buildings if b.building_type == "house"]
    destinations = [
        (15, 15),
        (15, 13),
        (15, 25),
        (15, 27),
        (15, 24),
        (15, 16),
    ]

    citizens = [
        Doctor(name="Dr. Rao", age=45),
        Teacher(name="Ms. Iyer", age=38),
        Shopkeeper(name="Raj", age=50),
        OfficeWorker(name="Priya", age=29),
        Student(name="Aarav", age=16),
        Citizen(name="Generic", age=30),
    ]

    for citizen, start, goal in zip(citizens, house_starts, destinations):
        citizen.y, citizen.x = start
        path = astar(start, goal, grid, state.road_closures)
        citizen.set_path(path)
        state.add_citizen(citizen)


async def run_simulation(websocket: WebSocket):
    initialize_city_state(city_state)
    sim_control.start()

    while True:
        if sim_control.running:
            city_state.update()

            time_of_day = city_state.clock.get_time_period()
            events = build_event_flags(weather=city_state.weather, tax_state=city_state.tax_state)

            for c in city_state.citizens:
                c.advance()
                think(c, tax_state=city_state.tax_state, time_of_day=time_of_day, events=events)

        state = {
            "grid_size": len(city_state.grid),
            "grid": city_state.grid,
            "agents": [c.to_dict() for c in city_state.citizens],
            "hour": city_state.clock.hour,
            "day": city_state.clock.day,
            "weather": city_state.weather.current_state,
            "taxActive": city_state.tax_state.active,
            "roadClosureActive": bool(city_state.road_closures.closed_road_ids()),
            "closedRoadIds": city_state.road_closures.closed_road_ids(),
        }

        await websocket.send_json(state)
        await asyncio.sleep(0.3)
      
