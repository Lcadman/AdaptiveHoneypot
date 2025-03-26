from bandit.bandit import EpsilonGreedyBandit
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time

import random

# Define the possible dwell times (in minutes)
dwell_times = [5, 8, 10, 12]

# Initialize the bandit algorithm (using epsilon-greedy)
bandit = EpsilonGreedyBandit(dwell_times, epsilon=0.2, alpha=0.1)

# Parse the historical tcp_syn data
data_file = 'data/Bitwarden Data Mar 18 2025.json'
df = parse_tcp_syn_data(data_file)

# Simulation loop: Each round simulates a honeypot run with a selected dwell time
num_rounds = 10

for i in range(num_rounds):
    print(f"\n--- Simulation Round {i+1} ---")
    # Step 1: Bandit selects a dwell time
    selected_dwell = bandit.select_action()
    
    # Step 2: Compute a reward for the selected dwell time
    # (In real deployment, this would come from actual honeypot performance; simulate using historical data for now)
    reward_value = compute_reward_for_dwell_time(df, selected_dwell)
    print(f"Simulated reward for {selected_dwell} minutes: {reward_value:.3f}")
    
    # Step 3: Update the bandit's estimates based on the observed reward
    bandit.update(selected_dwell, reward_value)