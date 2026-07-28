from app.models.citizen import Citizen
from app.ai.brain import think

def test_normal_citizen_uses_rules():
    c = Citizen("A", 20)
    c.energy = 20
    assert think(c) == "go_home"

def test_learning_citizen_without_learner_falls_back():
    c = Citizen("B", 22, occupation="learning_agent")
    assert think(c) == "go_home" if c.energy < 30 else True

from app.ai.learning import QLearner
from app.ai.memory import Memory

def test_learning_citizen_uses_qlearner():
    c = Citizen("D", 22, occupation="learning_agent")
    c.hunger = 90

    learner = QLearner(actions=["go_home", "go_restaurant", "go_work", "idle"])
    memory = Memory()

    action = think(c, learner=learner, memory=memory)

    assert action in learner.actions
    assert len(memory.recent()) == 1
    assert len(learner.q_table) > 0
