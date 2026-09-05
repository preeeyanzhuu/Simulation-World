from app.ai.learning import QLearner

def test_learns_to_eat_when_hungry():
    actions = ["eat", "rest", "work", "idle"]
    learner = QLearner(actions)

    state = ("medium", "high", "medium", "morning")
    next_state = ("medium", "low", "medium", "morning")

    for _ in range(2000):
        action = learner.choose_action(state)
        reward = 1 if action == "eat" else -0.1
        learner.update(state, action, reward, next_state)

    best_action = max(actions, key=lambda a: learner.get_q(state, a))
    assert best_action == "eat"
