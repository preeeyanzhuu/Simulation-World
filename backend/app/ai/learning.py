from app.ai.currency import get_currency
import random

class QLearner:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = {}
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self.actions, key=lambda a: self.get_q(state, a))

    def update(self, state, action, reward, next_state):
        old_q = self.get_q(state, action)
        best_next = max(self.get_q(next_state, a) for a in self.actions)
        new_q = old_q + self.alpha * (reward + self.gamma * best_next - old_q)
        self.q_table[(state, action)] = new_q

def calculate_reward(citizen, action, tax_state=None):

    currency = get_currency(citizen)
    reward = -0.05

    if action == "go_restaurant" and citizen.hunger > 70:
        reward += 1  

    if action == "go_mall" and citizen.happiness < 30:
        reward +=1
          
    if action == "go_work" and citizen.money < 10 and citizen.occupation != "student":
        work_bonus = 1

        if tax_state is not None and tax_state.active:
            work_bonus *= tax_state.multiplier
        reward += work_bonus

    if action == "go_school" and citizen.occupation == "student" and currency <10:
        reward +=1
    
    if action == "go_home" and citizen.energy < 30:
        reward += 1
    if citizen.energy <= 0:
        reward -= 2
    return reward

def get_state(citizen, time_of_day="morning",events=None):

    events = events or {}
    def bucket(value, low_cut, high_cut):
        if value < low_cut:
            return "low"
        elif value < high_cut:
            return "medium"
        return "high"

    return (
        bucket(citizen.energy, 30, 70),
        bucket(citizen.hunger, 30, 70),
        bucket(citizen.money, 10, 50),
        time_of_day,
        events.get("is_raining",False),
        events.get("tax_hike",False)
        )
    
    


def build_event_flags(weather=None, tax_state = None):
    return{
        "is_raining": weather.is_raining() if weather is not None else False,
        "tax_hike" : tax_state.active if tax_state is not None else False,
    }
