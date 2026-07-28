from app.models.citizen import Citizen
from app.ai.decision import decide

def test_low_energy_goes_home():
    c = Citizen("A", 20)
    c.energy = 20
    assert decide(c) == "go_home"

def test_hungry_goes_restaurant():
    c = Citizen("B", 20)
    c.energy = 80
    c.hunger = 90
    assert decide(c) == "go_restaurant"
