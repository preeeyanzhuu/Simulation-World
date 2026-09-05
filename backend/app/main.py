from fastapi import FastAPI
from world.city import create_grid
from engine.scheduler import SimClock
from engine.pathfinding import astar
from models.building import Hospital, School, Office, Park, Restaurant, Shop, House

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "server is alive"}

from fastapi import WebSocket
import asyncio 



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    grid = create_grid()
    clock = SimClock()

    #buildings
    h = Hospital((10,10), 10)
    s = School((15,15), 20)
    park_locations = [(5, 20), (10, 25)]
    for location in park_locations:
        park = Park(location, 30)
        for cell in park.get_occupied_cells():
            row = cell[0]
            col = cell[1]
            grid[row][col] = {"type": "building", "name": park.to_dict()}

    restaurant_locations = [(20, 5), (25, 10)]
    for location in restaurant_locations:
        restaurant = Restaurant(location, 20)
        for cell in restaurant.get_occupied_cells():
            row = cell[0]
            col = cell[1]
            grid[row][col] = {"type": "building", "name": restaurant.to_dict()}

    office_locations =[(8, 8), (18, 18)]
    for location in office_locations:
        office = Office(location, 50)
        for cell in office.get_occupied_cells():
            row = cell[0]
            col = cell[1]
            grid[row][col] = {"type": "building", "name": office.to_dict()}


    shop_locations = [(12, 5), (22, 12)]
    for location in shop_locations:
        shop = Shop(location, 10)
        for cell in shop.get_occupied_cells():
            row = cell[0]
            col = cell[1]
            grid[row][col] = {"type": "building", "name": shop.to_dict()}

    house_locations =[(2,2), (2,5), (2,8), (2,11), (2,14)]
    for location in house_locations:
        house = House(location, 4)
        for cell in house.get_occupied_cells():
            row = cell[0]
            col = cell[1]
            grid[row][col] = {"type": "building", "name": house.to_dict()}

    for cell in h.get_occupied_cells():
        row = cell[0]
        col = cell[1]
        grid[row][col] = {"type": "building", "name": h.to_dict()}

    for cell in s.get_occupied_cells():
        row = cell[0]
        col = cell[1]
        grid[row][col] = {"type": "building", "name": s.to_dict()}

    
    grid[5][5] = {"type": "road"}
    
    grid[5][6] = {"type": "building"}

    start = (5,0)
    goal = (7,10)
    path = astar(start,goal,grid)
    path1 = astar((5,10), (11,17), grid)
    path3 = astar((6,3), (29,29), grid)
    path4 = astar((0,0), (9,18), grid)
    path5 = astar((1,1), (12,11), grid)
    path2 = astar((2,3), (7,8), grid)

    citizens = [
        {"x": 0, "y": 3, "type": "citizen", "path": path, "path_index": 0  },
        {"x": 10, "y": 5, "type": "citizen", "path": path1, "path_index": 0},
        {"x": 3, "y": 2, "type": "citizen", "path": path2, "path_index": 0},
        {"x": 3, "y": 6, "type": "citizen", "path": path3, "path_index": 0},
        {"x": 0, "y": 0, "type": "citizen", "path": path4, "path_index": 0},
        {"x": 1, "y": 1, "type": "citizen", "path": path5, "path_index": 0},
    ]

    tick = 0

    while True:
        tick += 1
        clock.update()
        print(clock.tick, clock.hour)
        for c in citizens:
            if "path" in c:
                if c["path_index"] < len(c["path"]):
                   step = c["path"][c["path_index"]]
                   c["y"] = step[0]
                   c["x"] = step[1]
                   c["path_index"] += 1

        state = {
            "grid_size": len(grid),
            "grid": grid,
            "agents": citizens,
            "hour": clock.hour
        }

        await websocket.send_json(state)
        await asyncio.sleep(0.3)
    
