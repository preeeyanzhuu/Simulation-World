from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.engine.simulation import run_simulation
from app.api.events import router as events_router
from app.api.agents import router as agents_router
from app.api.simulation import router as simulation_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(agents_router)
app.include_router(simulation_router)


@app.get("/")
def read_root():
    return {"message": "server is alive"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await run_simulation(websocket)
