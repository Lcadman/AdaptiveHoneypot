import time
import numpy as np
import csv
import json
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
from bandit.state_extractor import extract_state
from bandit.rl_agent import SimpleQAgent
import datetime


# Add the helper function for converting state for JSON serialization
def convert_state_for_json(state):
    """
    Convert any numpy arrays in the state dictionary to lists so it can be JSON serialized.
    """
    new_state = {}
    for k, v in state.items():
        if isinstance(v, np.ndarray):
            new_state[k] = v.tolist()
        else:
            new_state[k] = v
    return new_state


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

    # Define dwell times from 5 to 15 minutes (fine grid)
    dwell_times = np.linspace(5, 15, 21).tolist()
    agent = SimpleQAgent(dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1)

    # Generate a timestamp string, e.g., "20250326_100458"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/controller_output_{timestamp}.csv"

    # Then open the CSV file using this filename:
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["DstIP", "InitialState", "SelectedDwell", "Reward", "NextState"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        groups = df_all.groupby("DstIP")

        for dst, group_df in groups:
            print(f"\n--- Processing honeypot instance for destination IP: {dst} ---")

            state = extract_state(group_df)
            # Convert state for JSON serialization
            json_state = convert_state_for_json(state)
            print(f"Initial state: {json_state}")

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
            print(f"Next state: {convert_state_for_json(next_state)}")

            agent.update(state, selected_dwell, reward_value, next_state)

            # Log information to CSV, converting state to JSON-serializable format
            log_row = {
                "DstIP": dst,
                "InitialState": json.dumps(convert_state_for_json(state)),
                "SelectedDwell": selected_dwell,
                "Reward": reward_value,
                "NextState": json.dumps(convert_state_for_json(next_state)),
            }
            writer.writerow(log_row)

            print("Honeypot instance completed. Moving to next instance...\n")
            time.sleep(1)


if __name__ == "__main__":
    main()
