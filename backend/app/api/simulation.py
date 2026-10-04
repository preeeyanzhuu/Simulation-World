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
        from app.engine.simulation import initialize_city_state
        from app.models.citizen import Citizen

        fresh = CityState()
        city_state.__dict__.clear()
        city_state.__dict__.update(fresh.__dict__)
        Citizen.reset_id_counter()
        initialize_city_state(city_state, force=True)
        self.running = True
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
    return {
        "running": running,
        "hour": city_state.clock.hour,
        "day": city_state.clock.day,
        "citizen_count": len(city_state.citizens),
    }


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
