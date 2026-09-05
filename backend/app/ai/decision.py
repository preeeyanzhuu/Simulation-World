from app.models.citizen import Citizen
from app.ai.currency import get_currency

def decide(citizen:Citizen):
    currency = get_currency(citizen)

    if citizen.energy<30:
        return "go_home"
    elif citizen.hunger>70:
        return "go_restaurant"
    elif citizen.happiness < 30:
        return "go_mall"
    elif currency < 10:
        return "go_school" if citizen.occupation == "student" else "go_work"
    

    else:
        return "idle"
