from app.models.citizen import Citizen
from app.ai.currency import get_currency

MEAL_PRICE = 10          # keep in sync with RESTAURANT_COST in engine/simulation.py


def _earn_money(citizen):
    return "go_school" if citizen.occupation == "student" else "go_work"


def decide(citizen: Citizen):
    money = get_currency(citizen)

    if citizen.energy < 30:
        return "go_home"
    elif citizen.hunger > 70:
        return "go_restaurant" if money >= MEAL_PRICE else _earn_money(citizen)
    elif citizen.happiness < 30:
        return "go_park" if money < 30 else "go_mall"
    elif money < 10:
        return _earn_money(citizen)
    else:
        return "idle"
