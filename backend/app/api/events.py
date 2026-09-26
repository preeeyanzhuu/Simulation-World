from fastapi import APIRouter
from pydantic import BaseModel

from app.world.state import city_state
from app.events.rain import trigger_rain
from app.events.tax import trigger_tax_hike, DEFAULT_TAX_HIKE_DURATION_TICKS, DEFAULT_TAX_HIKE_MULTIPLIER
from app.events.traffic import trigger_road_closure, DEFAULT_CLOSURE_DURATION_TICKS

router = APIRouter(prefix="/events", tags=["events"])


class RainRequest(BaseModel):
    duration_ticks: int = 20


class TaxHikeRequest(BaseModel):
    duration_ticks: int = DEFAULT_TAX_HIKE_DURATION_TICKS
    multiplier: float = DEFAULT_TAX_HIKE_MULTIPLIER


class RoadClosureRequest(BaseModel):
    road_id: str
    duration_ticks: int = DEFAULT_CLOSURE_DURATION_TICKS


@router.post("/rain")
def rain(req: RainRequest = RainRequest()):
    new_state = trigger_rain(city_state.weather, duration_ticks=req.duration_ticks)
    return {"weather": new_state, "duration_ticks": req.duration_ticks}


@router.post("/tax-hike")
def tax_hike(req: TaxHikeRequest = TaxHikeRequest()):
    active = trigger_tax_hike(
        city_state.tax_state,
        duration_ticks=req.duration_ticks,
        multiplier=req.multiplier,
    )
    return {
        "tax_active": active,
        "multiplier": city_state.tax_state.multiplier,
        "duration_ticks": req.duration_ticks,
    }


@router.post("/road-closure")
def road_closure(req: RoadClosureRequest):
    closed = trigger_road_closure(
        city_state.road_closures,
        req.road_id,
        duration_ticks=req.duration_ticks,
    )
    return {"road_id": req.road_id, "closed": closed, "duration_ticks": req.duration_ticks}
