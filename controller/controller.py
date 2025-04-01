import time
import numpy as np
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
from bandit.state_extractor import extract_state
from bandit.rl_agent import SimpleQAgent

# For simulation, we'll use historical data as the feed
DATA_FILE = "data/Bitwarden Data Mar 18 2025.json"


def simulate_honeypot_instance(dwell_time, df):
    dwell_time_seconds = dwell_time * 60
    simulated_data = df[df["TimeSinceStart"] <= dwell_time_seconds]
    return simulated_data


def simulate_overlap_data(dwell_time, df):
    dwell_time_seconds = dwell_time * 60
    overlap_data = df[df["TimeSinceStart"] > dwell_time_seconds]
    return overlap_data


def main():
    df_all = parse_tcp_syn_data(DATA_FILE)

    dwell_times = np.linspace(5, 15, 21).tolist()
    agent = SimpleQAgent(dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1)

    groups = df_all.groupby("DstIP")

    for dst, group_df in groups:
        print(f"\n--- Processing honeypot instance for destination IP: {dst} ---")

        state = extract_state(group_df)
        print(f"Initial state: {state}")

        selected_dwell = agent.select_action(state)
        print(f"Selected dwell time: {selected_dwell} minutes")

        simulated_data = simulate_honeypot_instance(selected_dwell, group_df)

        overlap_data = simulate_overlap_data(selected_dwell, group_df)
        reward_value = compute_reward_for_dwell_time(
            simulated_data, selected_dwell, alpha=1.0, beta=0.5, gamma=0.2
        )
        print(f"Computed reward for {selected_dwell} minutes: {reward_value:.3f}")

        if not overlap_data.empty:
            next_state = extract_state(overlap_data)
        else:
            next_state = {k: 0 for k in state}
        print(f"Next state: {next_state}")

        agent.update(state, selected_dwell, reward_value, next_state)

        print("Honeypot instance completed. Moving to next instance...\n")
        time.sleep(1)


if __name__ == "__main__":
    main()
