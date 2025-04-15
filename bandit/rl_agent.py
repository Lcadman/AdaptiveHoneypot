import random
import numpy as np
import pickle


class SimpleQAgent:
    def __init__(self, dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1, save_file=None):
        self.dwell_times = dwell_times
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}

        self.save_file = save_file

        if self.save_file is not None:
            try:
                with open(self.save_file, "rb") as f:
                    self.q_table = pickle.load(f)
                print("Loaded persistent Q-table")
            except FileNotFoundError:
                print("No persistent Q-table found, starting fresh")

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
            self.q_table[state_tuple] = {action: 0.0 for action in self.dwell_times}
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
        self.save_q_table()

    def save_q_table(self):
        if self.save_file is not None:
            with open(self.save_file, "wb") as f:
                pickle.dump(self.q_table, f)
            print("Saved persistent Q-table")
