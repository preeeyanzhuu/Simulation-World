from fastapi import APIRouter, HTTPException

from app.world.state import city_state

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def list_agents():
    return {
        "count": len(city_state.citizens),
        "agents": [c.to_dict() for c in city_state.citizens],
    }


@router.get("/{name}")
def get_agent(name: str):
    for c in city_state.citizens:
        if c.name == name:
            return c.to_dict()
    raise HTTPException(status_code=404, detail=f"No agent named {name!r}")
