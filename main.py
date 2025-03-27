import numpy as np
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
from bandit.bandit import UCBBandit

# Create a fine grid of dwell times from 5 to 15 minutes (e.g., in 0.5-minute increments)
dwell_times = np.linspace(5, 15, 21).tolist()  # 21 values: 5.0, 5.5, ..., 15.0
print("Possible dwell times:", dwell_times)

# Initialize the UCB bandit with the defined range
bandit = UCBBandit(dwell_times, c=1.0)

# Parse the historical tcp_syn data
data_file = 'data/Bitwarden Data Mar 18 2025.json'
df = parse_tcp_syn_data(data_file)

# Group the data by destination IP (DstIP) to simulate separate honeypot sessions.
# You might also want to split further if TimeSinceStart resets occur within the same DstIP.
groups = df.groupby('DstIP')

# Process each group (each honeypot instance)
for dst, group_df in groups:
    print(f"\n--- Simulating honeypot instance for destination IP: {dst} ---")
    
    # (Optional) Further splitting by checking if 'TimeSinceStart' resets within the group.
    # For now, we assume each group is a single honeypot instance.
    
    # Use UCB to select a dwell time
    selected_dwell = bandit.select_action()
    print(f"Selected dwell time: {selected_dwell:.2f} minutes")
    
    # Compute reward for this honeypot instance using our sophisticated reward function.
    # Hyperparameters (alpha, beta, gamma) can be tuned as needed.
    reward_value = compute_reward_for_dwell_time(group_df, selected_dwell, alpha=1.0, beta=0.5, gamma=0.2)
    print(f"Computed reward for {selected_dwell:.2f} minutes: {reward_value:.3f}")
    
    # Update the UCB bandit with the observed reward.
    bandit.update(selected_dwell, reward_value)