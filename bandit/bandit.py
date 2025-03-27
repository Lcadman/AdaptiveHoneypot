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


class UCBBandit:
    def __init__(self, dwell_times, c=1.0):
        """
        Initialize the UCB bandit with a list of possible dwell times (in minutes)
        and an exploration parameter c.
        
        Parameters:
          dwell_times: list of possible dwell times (floats), e.g., [5.0, 5.5, ..., 15.0]
          c: exploration parameter controlling the width of the confidence interval.
        """
        self.dwell_times = dwell_times
        self.c = c
        self.counts = {dt: 0 for dt in dwell_times}   # Number of times each dwell time was chosen.
        self.values = {dt: 0.0 for dt in dwell_times}   # Estimated average reward for each dwell time.
        self.total_count = 0  # Total number of selections.

    def select_action(self):
        """
        Select a dwell time using the UCB formula.
        Returns the dwell time with the highest UCB value.
        """
        self.total_count += 1
        ucb_values = {}
        # Ensure each dwell time is tried at least once.
        for dt in self.dwell_times:
            if self.counts[dt] == 0:
                print(f"Selecting {dt:.2f} minutes because it has not been tried yet.")
                return dt
            bonus = self.c * math.sqrt(math.log(self.total_count) / self.counts[dt])
            ucb_values[dt] = self.values[dt] + bonus
        # Debug: print all UCB values.
        print(f"UCB values: {ucb_values}")
        chosen_dt = max(ucb_values, key=ucb_values.get)
        print(f"Selected dwell time: {chosen_dt:.2f} minutes based on UCB.")
        return chosen_dt
    
    def update(self, dwell_time, reward):
        """
        Update the estimated reward (Q-value) for the chosen dwell time.
        
        Parameters:
          dwell_time: the dwell time (in minutes) that was selected.
          reward: the observed reward.
        """
        self.counts[dwell_time] += 1
        # Incremental update of the Q-value (average reward)
        self.values[dwell_time] += (reward - self.values[dwell_time]) / self.counts[dwell_time]
        print(f"Updated Q-value for {dwell_time:.2f} minutes: {self.values[dwell_time]:.3f}")