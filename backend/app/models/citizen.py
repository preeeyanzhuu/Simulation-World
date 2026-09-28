import itertools

from app.ai.actions import ACTIONS
from app.ai.learning import QLearner
from app.ai.memory import Memory


class Citizen:

    _id_counter = itertools.count(1)
    HUNGER_DECAY_PER_TICK = 0.3
    ENERGY_DECAY_PER_TICK = 0.25

    def __init__(self, name, age, occupation="none"):
        self.id = next(Citizen._id_counter)
        self.name = name
        self.age = age
        self.occupation = occupation
        self.energy = 100
        self.hunger = 0
        self.money = 50
        self.happiness = 70
        self.x = 0
        self.y = 0
        self.path = []
        self.path_index = 0
        self.home_entrance = None
        self.current_action = None
        self.arrived_effect_done = False

    def set_path(self, path):
        self.path = path or []
        self.path_index = 0
        self.arrived_effect_done = False
        if self.path:
            self.y, self.x = self.path[0]

    def advance(self):
        if not self.is_alive:
            return

        if self.path and self.path_index < len(self.path) - 1:
            self.path_index += 1
            self.y, self.x = self.path[self.path_index]

        self.hunger = min(100, self.hunger + self.HUNGER_DECAY_PER_TICK)
        self.energy = max(0, self.energy - self.ENERGY_DECAY_PER_TICK)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "type": "learning" if self.occupation == "learning_agent" else "rule",
            "x": self.x,
            "y": self.y,
            "energy": round(self.energy, 1),
            "hunger": round(self.hunger, 1),
            "money": self.money,
            "happiness": self.happiness,
            "action": self.current_action,
        }

    def die(self, reason="unknown"):
        self.is_alive = False
        self.cause_of_death = reason

    def __repr__(self):
        status = "alive" if self.is_alive else f"dead ({self.cause_of_death})"
        return (f"{self.__class__.__name__}(name={self.name!r}, age={self.age}, "
                f"occupation={self.occupation!r}, energy={self.energy}, "
                f"hunger={self.hunger}, money={self.money}, "
                f"happiness={self.happiness}, status={status})")


class Doctor(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="doctor")
        self.workplace = "hospital"


class Teacher(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="teacher")
        self.workplace = "school"


class Shopkeeper(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="shopkeeper")
        self.workplace = "mall"


class OfficeWorker(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="office_worker")
        self.workplace = "office"


class Student(Citizen):
    def __init__(self, name, age, daily_allowance=15):
        super().__init__(name, age, occupation="student")
        self.workplace = "school"
        self.daily_allowance = daily_allowance

    def receive_allowance(self):
        self.money += self.daily_allowance


class LearningAgent(Citizen):
    def __init__(self, name, age, alpha=0.1, gamma=0.9, epsilon=0.2,
                 epsilon_min=0.02, epsilon_decay=0.9995):
        super().__init__(name, age, occupation="learning_agent")
        self.workplace = "office"
        self.learner = QLearner(
            actions=ACTIONS, alpha=alpha, gamma=gamma, epsilon=epsilon,
            epsilon_min=epsilon_min, epsilon_decay=epsilon_decay,
        )
        self.memory = Memory()
