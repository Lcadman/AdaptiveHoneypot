import numpy as np
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
from bandit.state_extractor import extract_state
import logging
import csv
import datetime
import json

# Set up the logger to output to both console and a file
logger = logging.getLogger('test_controller')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('logs/test_controller.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Path to your historical data file
DATA_FILE = "data/Bitwarden Data Mar 18 2025.json"

def convert_state_for_json(state):
    new_state = {}
    for k, v in state.items():
        if isinstance(v, np.ndarray):
            new_state[k] = v.tolist()
        else:
            new_state[k] = v
    return new_state

def test_dwell_times_for_instance(df_instance, dwell_range):
    dstip = df_instance["DstIP"].iloc[0]
    initial_state = extract_state(df_instance)
    # Convert state so it can be JSON serialized
    json_state = convert_state_for_json(initial_state)
    logger.info(f"\nTesting honeypot instance for DstIP: {dstip}")
    logger.info(f"Initial state: {json.dumps(json_state)}")
    rows = []
    for dwell in dwell_range:
        reward_value = compute_reward_for_dwell_time(df_instance, dwell, alpha=1.0, beta=0.5, gamma=0.2)
        rows.append({"DstIP": dstip, "DwellTime": dwell, "Reward": reward_value})
        logger.info(f"Dwell time: {dwell:.1f} minutes, Computed Reward: {reward_value:.3f}")
    optimal_row = max(rows, key=lambda row: row["Reward"])
    optimal_dwell = optimal_row["DwellTime"]
    optimal_reward = optimal_row["Reward"]
    logger.info(f"Optimal dwell time for this instance: {optimal_dwell:.1f} minutes with reward {optimal_reward:.3f}\n")
    return rows, optimal_dwell, optimal_reward, initial_state

def main():
    df_all = parse_tcp_syn_data(DATA_FILE)
    
    # Define the range of dwell times to test, e.g., from 5 to 15 minutes in 0.5 minute increments
    dwell_range = np.arange(5, 15.5, 0.5)  # 5, 5.5, 6, ..., 15
    
    # Generate a filename with date and time
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"logs/dwell_rewards_{timestamp}.csv"
    
    # Open a CSV file to write the output
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["DstIP", "DwellTime", "Reward", "OptimalDwell", "OptimalReward", "InitialState"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Group data by DstIP, assuming each group corresponds to one honeypot instance
        groups = df_all.groupby("DstIP")
        for dst, group_df in groups:
            rows, optimal_dwell, optimal_reward, initial_state = test_dwell_times_for_instance(group_df, dwell_range)
            for row in rows:
                row["OptimalDwell"] = optimal_dwell
                row["OptimalReward"] = optimal_reward
                # Convert state to JSON-serializable string
                row["InitialState"] = json.dumps(convert_state_for_json(initial_state))
                writer.writerow(row)

if __name__ == "__main__":
    main()