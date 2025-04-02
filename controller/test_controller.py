import numpy as np
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time
import logging
import csv

# Set up the logger to output to both console and a file
logger = logging.getLogger('test_controller')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('test_controller.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Path to your historical data file
DATA_FILE = "data/Bitwarden Data Mar 18 2025.json"

def test_dwell_times_for_instance(df_instance, dwell_range):
    dstip = df_instance["DstIP"].iloc[0]
    logger.info(f"\nTesting honeypot instance for DstIP: {dstip}")
    rows = []
    for dwell in dwell_range:
        reward_value = compute_reward_for_dwell_time(df_instance, dwell, alpha=1.0, beta=0.5, gamma=0.2)
        rows.append({"DstIP": dstip, "DwellTime": dwell, "Reward": reward_value})
        logger.info(f"Dwell time: {dwell:.1f} minutes, Computed Reward: {reward_value:.3f}")
    optimal_dwell = max(rows, key=lambda row: row["Reward"])["DwellTime"]
    logger.info(f"Optimal dwell time for this instance: {optimal_dwell:.1f} minutes with reward {max(rows, key=lambda row: row['Reward'])['Reward']:.3f}\n")
    return rows, optimal_dwell

def main():
    df_all = parse_tcp_syn_data(DATA_FILE)
    
    # Define the range of dwell times to test, e.g., from 5 to 15 minutes in 0.5 minute increments
    dwell_range = np.arange(5, 15.5, 0.5)  # 5, 5.5, 6, ..., 15
    
    # Group data by DstIP, assuming each group corresponds to one honeypot instance
    groups = df_all.groupby("DstIP")
    
    # Open a CSV file to write the output
    with open("dwell_rewards.csv", "w", newline="") as csvfile:
        fieldnames = ["DstIP", "DwellTime", "Reward"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # For each honeypot instance, test all dwell times and write the results to CSV
        for dst, group_df in groups:
            rows, optimal_dwell = test_dwell_times_for_instance(group_df, dwell_range)
            for row in rows:
                writer.writerow(row)

if __name__ == "__main__":
    main()