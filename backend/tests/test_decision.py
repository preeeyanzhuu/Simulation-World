from app.models.citizen import Citizen
from app.ai.decision import decide

low_energy = Citizen("A", 20)
low_energy.energy = 20

hungry = Citizen("B", 20)
hungry.energy = 80
hungry.hunger = 90

assert decide(low_energy) == "go_home"
assert decide(hungry) == "go_restaurant"

print("ALL TESTS PASSED")
