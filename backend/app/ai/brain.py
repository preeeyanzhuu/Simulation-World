from app.models.citizen import Citizen
from app.ai.decision import decide
from app.ai.learning import get_state, calculate_reward

def think(citizen: Citizen, learner=None, memory=None, time_of_day="morning"):
    if citizen.occupation == "learning_agent" and learner is not None:
        state = get_state(citizen, time_of_day)
        action = learner.choose_action(state)
        reward = calculate_reward(citizen, action)
        next_state = get_state(citizen, time_of_day)
        learner.update(state, action, reward, next_state)

        if memory is not None:
            memory.add((state, action, reward))

        return action

    return decide(citizen)
