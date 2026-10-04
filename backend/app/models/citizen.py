import itertools
import os

from app.ai.actions import ACTIONS
from app.ai.learning import QLearner
from app.ai.memory import Memory


def _xy(cell):
    return {"x": cell[1], "y": cell[0]} if cell else None
Q_TABLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "q_tables")


class Citizen:

    _id_counter = itertools.count(1)
    HUNGER_DECAY_PER_TICK = 0.3
    ENERGY_DECAY_PER_TICK = 0.25
    HAPPINESS_DECAY_PER_TICK = 0.1
    DEATH_GRACE_TICKS = 240    

    @classmethod
    def reset_id_counter(cls):
        cls._id_counter = itertools.count(1)

    def __init__(self, name, age, occupation="none"):
        self.id = next(Citizen._id_counter)
        self.name = name
        self.age = age
        self.occupation = occupation
        self.energy = 100
        self.hunger = 0
        self.money = 50
        self.happiness = 70
        self.is_alive = True
        self.cause_of_death = None
        self.x = 0
        self.y = 0
        self.path = []
        self.path_index = 0
        self.home_entrance = None
        self.current_action = None
        self.arrived_effect_done = False
        self.last_reward = 0.0      
        self.critical_ticks = 0  

    def set_path(self, path):
        self.path = path or []
        self.path_index = 0
        self.arrived_effect_done = False
        if self.path:
            self.y, self.x = self.path[0]

    def advance(self, can_move=True):
        if not self.is_alive:
            return

        if can_move and self.path and self.path_index < len(self.path) - 1:
            nxt = self.path[self.path_index + 1]
            self.path_index += 1
            self.y, self.x = nxt

        self.hunger = min(100, self.hunger + self.HUNGER_DECAY_PER_TICK)
        self.energy = max(0, self.energy - self.ENERGY_DECAY_PER_TICK)
        self.happiness = max(0, self.happiness - self.HAPPINESS_DECAY_PER_TICK)

        if self.hunger >= 100 or self.energy <= 0:
            self.critical_ticks += 1
            if self.critical_ticks >= self.DEATH_GRACE_TICKS:
                reason = "starvation" if self.hunger >= 100 else "exhaustion"
                self.die(reason)
        else:
            self.critical_ticks = 0

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
            "money": round(self.money, 1),
            "happiness": round(self.happiness, 1),
            "is_alive": self.is_alive,
            "cause_of_death": self.cause_of_death,
            "action": self.current_action,
            "workplace": getattr(self, "workplace", None),
            "home": _xy(self.home_entrance),
            "goal": _xy(self.path[-1]) if self.path else None,
            "progress": [self.path_index, len(self.path)],
            "last_reward": round(self.last_reward, 2),
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
    DEFAULT_Q_PATH = os.path.join(Q_TABLE_DIR, "q_table_learning.csv")

    def __init__(self, name, age, alpha=0.1, gamma=0.9, epsilon=0.2,
                 epsilon_min=0.02, epsilon_decay=0.9995, q_table_path=None):
        super().__init__(name, age, occupation="learning_agent")
        self.workplace = "office"
        self.learner = QLearner(
            actions=ACTIONS, alpha=alpha, gamma=gamma, epsilon=epsilon,
            epsilon_min=epsilon_min, epsilon_decay=epsilon_decay,
        )
        self.memory = Memory()
        path = q_table_path or self.DEFAULT_Q_PATH
        self.learner.load_q_table(path)

    def save_learning(self, path=None):
        path = path or self.DEFAULT_Q_PATH
        self.learner.save_q_table(path)

    def to_dict(self):
        data = super().to_dict()
        recent = self.memory.recent()   
        data["learner"] = {
            "epsilon": round(self.learner.epsilon, 3),
            "steps": self.learner.steps,
            "q_entries": len(self.learner.q_table),
            "last_state": list(recent[-1][0]) if recent else None,
            "recent": [
                {"action": action, "reward": round(reward, 2)}
                for (_state, action, reward) in recent
            ],
        }
        return data
