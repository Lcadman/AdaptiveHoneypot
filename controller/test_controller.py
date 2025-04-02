import numpy as np
from data.data_parser import parse_tcp_syn_data
from bandit.reward import compute_reward_for_dwell_time

# Path to your historical data file
DATA_FILE = "data/Bitwarden Data Mar 18 2025.json"

def test_dwell_times_for_instance(df_instance, dwell_range):
    print(f"\nTesting honeypot instance for DstIP: {df_instance['DstIP'].iloc[0]}")
    rewards = {}
    for dwell in dwell_range:
        reward_value = compute_reward_for_dwell_time(df_instance, dwell, alpha=1.0, beta=0.5, gamma=0.2)
        rewards[dwell] = reward_value
        print(f"Dwell time: {dwell:.1f} minutes, Computed Reward: {reward_value:.3f}")
    optimal_dwell = max(rewards, key=rewards.get)
    print(f"Optimal dwell time for this instance: {optimal_dwell:.1f} minutes with reward {rewards[optimal_dwell]:.3f}\n")
    return optimal_dwell, rewards

def main():
    df_all = parse_tcp_syn_data(DATA_FILE)
    
    # Define the range of dwell times to test, e.g., from 5 to 15 minutes in 0.5 minute increments
    dwell_range = np.arange(5, 15.5, 0.5)  # 5, 5.5, 6, ..., 15
    
    # Group data by DstIP, assuming each group corresponds to one honeypot instance
    groups = df_all.groupby("DstIP")
    
    # For each honeypot instance, test all dwell times and determine the optimal one
    for dst, group_df in groups:
        test_dwell_times_for_instance(group_df, dwell_range)

if __name__ == "__main__":
    main()