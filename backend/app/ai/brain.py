from app.models.citizen import Citizen
from app.ai.decision import decide

def think(citizen:Citizen,learner=None):
    if citizen.occupation=="learning_agent" and learner is not None:
        return "idle"
    return(decide(citizen))
