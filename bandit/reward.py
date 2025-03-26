import numpy as np

def compute_reward_for_dwell_time(df, dwell_time):
    """
    Compute a reward for a given dwell time based on historical data in DataFrame df.
    Here, we compute reward as:
      reward = (number of unique SrcIP up to dwell_time seconds) / dwell_time
    dwell_time is given in minutes.
    """
    dwell_time_seconds = dwell_time * 60
    # Filter the DataFrame for records within the dwell time
    filtered_df = df[df['TimeSinceStart'] <= dwell_time_seconds]
    # Count unique source IPs as a simple metric for threat capture
    unique_ips = filtered_df['SrcIP'].nunique()
    # Normalize the reward by dwell time to penalize overly long durations if necessary
    reward = unique_ips / dwell_time
    return reward

# Simple test
if __name__ == '__main__':
    from data.data_parser import parse_tcp_syn_data
    df = parse_tcp_syn_data('../data/Bitwarden Data Mar 18 2025.json')
    sample_dwell = 10  # minutes
    r = compute_reward_for_dwell_time(df, sample_dwell)
    print(f"Reward for {sample_dwell} minutes dwell time: {r:.3f}")