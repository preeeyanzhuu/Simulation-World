from app.models.citizen import Citizen
from app.ai.decision import decide
from app.ai.learning import get_state


def think(citizen: Citizen, learner=None, memory=None, time_of_day="morning",
          tax_state=None, events=None, allowed_actions=None):

    if citizen.occupation == "learning_agent" and learner is not None:
        state = get_state(citizen, time_of_day, events=events)
        action = learner.choose_action(state, allowed=allowed_actions)

        learner.begin_action(state, action)
        if memory is not None:
            memory.add((state, action, 0.0))
        return action

    return decide(citizen)
