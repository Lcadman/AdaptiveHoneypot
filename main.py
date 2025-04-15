from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
from bandit.state_extractor import extract_state
from bandit.rl_agent import SimpleQAgent
import numpy as np

# Define a range of possible dwell times (e.g., 5 to 15 minutes in 0.5 minute increments)
dwell_times = np.linspace(5, 15, 21).tolist()
print("Possible dwell times:", dwell_times)

# Initialize the RL agent.
agent = SimpleQAgent(dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1)

# Parse the historical tcp_syn data.
data_file = "data/Bitwarden Data Mar 18 2025.json"
df = parse_tcp_syn_data(data_file)

# Group data by honeypot instance (assuming each unique DstIP indicates a session).
groups = df.groupby("DstIP")

# For each honeypot session, simulate the decision-making process.
for dst, group_df in groups:
    print(f"\n--- Processing honeypot instance for destination IP: {dst} ---")

    # Extract the initial state from the entire session.
    state = extract_state(group_df)
    print(f"Initial state: {state}")

    # The agent selects a dwell time based on the current state.
    selected_dwell = agent.select_action(state)
    print(f"Selected dwell time: {selected_dwell} minutes")

    # Compute the reward if the honeypot had been run for the selected dwell time.
    reward_value = compute_reward_for_dwell_time(
        group_df, selected_dwell, alpha=1.0, beta=0.5, gamma=0.2
    )
    print(f"Computed reward for {selected_dwell} minutes: {reward_value:.3f}")

    # Simulate the "next state" by considering only data after the selected dwell time.
    dwell_time_seconds = selected_dwell * 60
    next_group_df = group_df[group_df["TimeSinceStart"] > dwell_time_seconds]
    if not next_group_df.empty:
        next_state = extract_state(next_group_df)
    else:
        # If there is no remaining data, we use the current state (or a zero state) as a fallback.
        next_state = {k: 0 for k in state}

    print(f"Next state: {next_state}")

    # Update the RL agent with the transition.
    agent.update(state, selected_dwell, reward_value, next_state)
