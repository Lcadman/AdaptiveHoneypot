import random
import numpy as np


class SimpleQAgent:
    def __init__(self, dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.dwell_times = dwell_times
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}

    def discretize_state(self, state):
        state_tuple = []
        for k in sorted(state.keys()):
            val = state[k]
            if isinstance(val, np.ndarray):
                val = tuple(np.round(val, 2).tolist())
            else:
                try:
                    val = round(val, 2)
                except Exception:
                    pass
            state_tuple.append(val)
        return tuple(state_tuple)

    def get_q_values(self, state_tuple):
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = {action: action for action in self.dwell_times}
        return self.q_table[state_tuple]

    def select_action(self, state):
        state_tuple = self.discretize_state(state)
        q_values = self.get_q_values(state_tuple)

        if random.random() < self.epsilon:
            action = random.choice(self.dwell_times)
            print(f"Exploring: Selected random dwell time: {action} minutes")
        else:
            action = max(q_values, key=q_values.get)
            print(f"Exploiting: Selected dwell time: {action} minutes")
        return action

    def update(self, state, action, reward, next_state):
        state_tuple = self.discretize_state(state)
        next_state_tuple = self.discretize_state(next_state)

        current_q = self.get_q_values(state_tuple)[action]
        next_q_values = self.get_q_values(next_state_tuple)
        best_next_q = max(next_q_values.values())

        new_q = current_q + self.alpha * (reward + self.gamma * best_next_q - current_q)
        self.q_table[state_tuple][action] = new_q

        print(f"Updated Q-value for state {state_tuple}, action {action}: {new_q:.3f}")
