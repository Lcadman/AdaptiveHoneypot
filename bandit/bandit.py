import random
import math

class EpsilonGreedyBandit:
    def __init__(self, dwell_times, epsilon=0.1, alpha=0.1):
        """
        Initialize the bandit with a list of dwell times (in minutes),
        an exploration rate (epsilon), and a learning rate (alpha).
        """
        self.dwell_times = dwell_times  # e.g., [5, 8, 10, 12]
        self.epsilon = epsilon
        self.alpha = alpha
        self.counts = {dt: 0 for dt in dwell_times}     # Count of selections for each dwell time
        self.values = {dt: 0.0 for dt in dwell_times}     # Estimated Q-values for each dwell time

    def select_action(self):
        """
        Choose a dwell time based on epsilon-greedy policy.
        """
        if random.random() < self.epsilon:
            # Explore: choose a random dwell time
            action = random.choice(self.dwell_times)
            print(f"Exploring: Selected random dwell time: {action} minutes")
        else:
            # Exploit: choose the dwell time with highest estimated reward
            action = max(self.dwell_times, key=lambda dt: self.values[dt])
            print(f"Exploiting: Selected best dwell time: {action} minutes")
        return action

    def update(self, dwell_time, reward):
        """
        Update the estimated reward for the chosen dwell time.
        """
        self.counts[dwell_time] += 1
        # Incremental update of Q-value
        self.values[dwell_time] += self.alpha * (reward - self.values[dwell_time])
        print(f"Updated Q-value for {dwell_time} minutes: {self.values[dwell_time]:.3f}")