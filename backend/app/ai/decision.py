from app.models.citizen import Citizen
def decide(citizen:Citizen):
    if citizen.energy<30:
        return "go_home"
    elif citizen.hunger>70:
        return "go_restaurant"
    elif citizen.money<10:
        return "go_work"
    else:
        return "idle"
