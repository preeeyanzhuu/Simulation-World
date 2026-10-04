from app.ai.currency import get_currency
import csv
import os
import random


class QLearner:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2,
                 epsilon_min=0.02, epsilon_decay=1.0):
        self.q_table = {}
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.steps = 0
        self._pending = None

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, allowed=None):
        pool = list(allowed) if allowed else list(self.actions)
        if not pool:
            return "idle"
        if random.random() < self.epsilon:
            return random.choice(pool)
        best_q = max(self.get_q(state, a) for a in pool)
        tied = [a for a in pool if self.get_q(state, a) == best_q]
        return random.choice(tied)

    def update(self, state, action, reward, next_state):
        old_q = self.get_q(state, action)
        best_next = max(self.get_q(next_state, a) for a in self.actions)
        new_q = old_q + self.alpha * (reward + self.gamma * best_next - old_q)
        self.q_table[(state, action)] = new_q

    def begin_action(self, state, action):
        self._pending = (state, action)
        self.steps += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def complete_action(self, reward, next_state):
        if self._pending is None:
            return
        prev_state, prev_action = self._pending
        self.update(prev_state, prev_action, reward, next_state)
        self._pending = None
    def observe(self, state, action, reward):
        if self._pending is not None:
            prev_state, prev_action, prev_reward = self._pending
            self.update(prev_state, prev_action, prev_reward, state)
        self._pending = (state, action, reward)
        self.steps += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self, path):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "energy", "hunger", "money", "happiness",
                "time_of_day", "is_raining", "tax_hike",
                "action", "q_value",
            ])
            for (state, action), q in sorted(
                self.q_table.items(), key=lambda kv: -kv[1]
            ):
                row = list(state) + [action, round(q, 6)]
                writer.writerow(row)

    def load_q_table(self, path):
        if not os.path.isfile(path):
            return 0
        loaded = 0
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    state = (
                        row["energy"],
                        row["hunger"],
                        row["money"],
                        row["happiness"],
                        row["time_of_day"],
                        row["is_raining"] in ("True", "true", "1"),
                        row["tax_hike"] in ("True", "true", "1"),
                    )
                    action = row["action"]
                    q = float(row["q_value"])
                    self.q_table[(state, action)] = q
                    loaded += 1
                except (KeyError, ValueError):
                    continue
        return loaded


def calculate_arrival_reward(citizen, action, tax_state=None, before=None):
    reward = 0.0

    if action == "go_restaurant":
        if before is not None and citizen.hunger < before.get("hunger", citizen.hunger):
            reward += 1.5
        elif citizen.hunger < 70:
            reward += 0.5
        else:
            reward -= 0.5

    elif action == "go_home":
        if before is not None and citizen.energy > before.get("energy", citizen.energy):
            reward += 1.5
        elif citizen.energy > 30:
            reward += 0.5

    elif action == "go_mall":
        if before is not None and citizen.happiness > before.get("happiness", citizen.happiness):
            reward += 1.0
        else:
            reward -= 0.3

    elif action == "go_park":
        if before is not None and citizen.happiness > before.get("happiness", citizen.happiness):
            reward += 1.2 

    elif action == "go_work" and citizen.occupation != "student":
        work_bonus = 1.0
        if tax_state is not None and tax_state.active:
            work_bonus *= tax_state.multiplier
        reward += work_bonus

    elif action == "go_school" and citizen.occupation == "student":
        reward += 1.0

    if citizen.energy <= 0 or citizen.hunger >= 100:
        reward -= 2.0

    return reward


def calculate_tick_penalty(citizen):
    reward = -0.02
    if citizen.energy <= 0:
        reward -= 0.5
    if citizen.hunger >= 100:
        reward -= 0.5
    if citizen.energy < 20:
        reward -= 0.1
    if citizen.hunger > 85:
        reward -= 0.1
    return reward
def calculate_reward(citizen, action, tax_state=None):
    currency = get_currency(citizen)
    reward = -0.05

    if action == "go_restaurant" and citizen.hunger > 70:
        reward += 1.0
    if action in ("go_mall", "go_park") and citizen.happiness < 30:
        reward += 1.0
    if action == "go_work" and citizen.money < 10 and citizen.occupation != "student":
        work_bonus = 1.0
        if tax_state is not None and tax_state.active:
            work_bonus *= tax_state.multiplier
        reward += work_bonus
    if action == "go_school" and citizen.occupation == "student" and currency < 10:
        reward += 1.0
    if action == "go_home" and citizen.energy < 30:
        reward += 1.0
    if citizen.energy <= 0:
        reward -= 2.0
    return reward


def get_state(citizen, time_of_day="morning", events=None):
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
        bucket(citizen.happiness, 20, 70),
        time_of_day,
        bool(events.get("is_raining", False)),
        bool(events.get("tax_hike", False)),
    )


def build_event_flags(weather=None, tax_state=None):
    return {
        "is_raining": weather.is_raining() if weather is not None else False,
        "tax_hike": tax_state.active if tax_state is not None else False,
    }
