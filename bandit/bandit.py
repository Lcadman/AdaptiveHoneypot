import random
import math


class EpsilonGreedyBandit:
    def __init__(self, dwell_times, epsilon=0.1, alpha=0.1):

        self.dwell_times = dwell_times
        self.epsilon = epsilon
        self.alpha = alpha
        self.counts = {dt: 0 for dt in dwell_times}
        self.values = {dt: 0.0 for dt in dwell_times}

    def select_action(self):

        if random.random() < self.epsilon:
            action = random.choice(self.dwell_times)
            print(f"Exploring: Selected random dwell time: {action} minutes")
        else:
            action = max(self.dwell_times, key=lambda dt: self.values[dt])
            print(f"Exploiting: Selected best dwell time: {action} minutes")
        return action

    def update(self, dwell_time, reward):
        self.counts[dwell_time] += 1
        self.values[dwell_time] += self.alpha * (reward - self.values[dwell_time])
        print(
            f"Updated Q-value for {dwell_time} minutes: {self.values[dwell_time]:.3f}"
        )


class UCBBandit:
    def __init__(self, dwell_times, c=1.0):
        self.dwell_times = dwell_times
        self.c = c
        self.counts = {dt: 0 for dt in dwell_times}
        self.values = {dt: 0.0 for dt in dwell_times}
        self.total_count = 0

    def select_action(self):
        self.total_count += 1
        ucb_values = {}

        for dt in self.dwell_times:
            if self.counts[dt] == 0:
                print(f"Selecting {dt:.2f} minutes because it has not been tried yet.")
                return dt
            bonus = self.c * math.sqrt(math.log(self.total_count) / self.counts[dt])
            ucb_values[dt] = self.values[dt] + bonus

        print(f"UCB values: {ucb_values}")
        chosen_dt = max(ucb_values, key=ucb_values.get)
        print(f"Selected dwell time: {chosen_dt:.2f} minutes based on UCB.")
        return chosen_dt

    def update(self, dwell_time, reward):
        self.counts[dwell_time] += 1

        self.values[dwell_time] += (reward - self.values[dwell_time]) / self.counts[
            dwell_time
        ]
        print(
            f"Updated Q-value for {dwell_time:.2f} minutes: {self.values[dwell_time]:.3f}"
        )
