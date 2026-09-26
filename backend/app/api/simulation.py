from fastapi import APIRouter

from app.world.state import city_state, CityState

router = APIRouter(prefix="/simulation", tags=["simulation"])


class SimulationControl:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        return self.running

    def stop(self):
        self.running = False
        return self.running

    def reset(self):
        self.running = False
        new_state = CityState()
        city_state.grid = new_state.grid
        city_state.clock = new_state.clock
        city_state.weather = new_state.weather
        city_state.tax_state = new_state.tax_state
        city_state.road_closures = new_state.road_closures
        city_state.citizens = new_state.citizens
        return self.running


sim_control = SimulationControl()


@router.post("/start")
def start_simulation():
    running = sim_control.start()
    return {"running": running}


@router.post("/stop")
def stop_simulation():
    running = sim_control.stop()
    return {"running": running}


@router.post("/reset")
def reset_simulation():
    running = sim_control.reset()
    return {"running": running, "hour": city_state.clock.hour, "day": city_state.clock.day}


@router.get("/status")
def simulation_status():
    return {
        "running": sim_control.running,
        "tick": city_state.clock.tick,
        "hour": city_state.clock.hour,
        "day": city_state.clock.day,
        "weather": city_state.weather.current_state,
        "tax_active": city_state.tax_state.active,
        "citizen_count": len(city_state.citizens),
    }
