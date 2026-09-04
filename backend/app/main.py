from fastapi import FastAPI
from world.city import create_grid
from engine.scheduler import SimClock
from engine.pathfinding import astar

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
    
    grid[5][5] = {"type": "road"}
    grid[10][10] = {"type": "building"}
    grid[5][6] = {"type": "building"}

    start = (5,0)
    goal = (7,10)
    path = astar(start,goal,grid)




    citizens = [
        {"x": 0, "y": 3, "type": "citizen", "path": path, "path_index": 0  }
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
            "grid_size": 20,
            "grid": grid,
            "agents": citizens,
            "hour": clock.hour
        }

        await websocket.send_json(state)
        await asyncio.sleep(0.3)
