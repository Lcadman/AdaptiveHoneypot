import numpy as np
import pandas as pd

def compute_reward_for_dwell_time(df, dwell_time, alpha=1.0, beta=1.0, gamma=1.0, session_gap=60):
    """
    Compute a reward for a given dwell time based on historical data in DataFrame df.
    
    The reward is computed as:
      reward = alpha * weighted_unique_ips + beta * weighted_session_count - gamma * duration_penalty
     
    where:
      - weighted_unique_ips is the sum over unique SrcIPs of their attack scores (e.g., max score per IP).
      - weighted_session_count is the total weighted number of sessions across all SrcIPs.
        For each session, we use the maximum attack score observed in that session.
      - duration_penalty is the dwell time (in minutes).
      
    Parameters:
      df: pandas DataFrame containing the tcp_syn data.
      dwell_time: dwell time in minutes.
      alpha, beta, gamma: hyperparameters for weighting the reward components.
      session_gap: gap in seconds to differentiate sessions.
      
    Returns:
      reward: the computed reward value.
    """
    dwell_time_seconds = dwell_time * 60
    # Filter data for the dwell time period
    filtered_df = df[df['TimeSinceStart'] <= dwell_time_seconds]
    
    # Compute weighted unique_ips:
    # For each unique SrcIP, compute the maximum attack score among its records.
    unique_ips = filtered_df['SrcIP'].unique()
    weighted_unique_ips = 0.0
    for ip in unique_ips:
        ip_records = filtered_df[filtered_df['SrcIP'] == ip]
        # Compute attack score for each record and take the max for that IP
        scores = ip_records.apply(compute_attack_score, axis=1)
        max_score = scores.max()
        weighted_unique_ips += max_score
    
    # Compute weighted session_count:
    weighted_session_count = 0.0
    grouped = filtered_df.groupby('SrcIP')
    for src, group in grouped:
        group = group.sort_values('TimeSinceStart')
        sessions = []
        current_session_scores = []
        last_time = None
        for idx, t in group['TimeSinceStart'].items():
            # Compute attack score for this record
            score = compute_attack_score(group.loc[idx])
            if last_time is None:
                current_session_scores.append(score)
                last_time = t
            else:
                if t - last_time > session_gap:
                    # End current session; store the max score of this session
                    sessions.append(max(current_session_scores))
                    current_session_scores = [score]
                else:
                    current_session_scores.append(score)
                last_time = t
        # Add the last session if exists
        if current_session_scores:
            sessions.append(max(current_session_scores))
        weighted_session_count += sum(sessions)
    
    # Duration penalty is simply the dwell time in minutes
    duration_penalty = dwell_time
    
    reward = alpha * weighted_unique_ips + beta * weighted_session_count - gamma * duration_penalty
    return reward

def compute_attack_score(row):
    """
    Compute an attack score for a single record.
    If the destination port is in a list of known target ports,
    assign a multiplier > 1; otherwise return 1.
    """
    # Example suspicious ports with associated weights.
    suspicious_ports = {
        22: 1.5,    # SSH
        23: 1.5,    # Telnet
        3389: 2.0,  # RDP
        80: 1.2,    # HTTP (sometimes targeted)
        443: 1.2    # HTTPS (sometimes targeted)
    }
    
    try:
        port = int(row['DstPort'])
    except (KeyError, ValueError):
        port = 0
    return suspicious_ports.get(port, 1.0)

# Simple test
if __name__ == '__main__':
    from data.data_parser import parse_tcp_syn_data
    # Adjust path if necessary
    df = parse_tcp_syn_data('data/Bitwarden Data Mar 18 2025.json')
    sample_dwell = 10  # dwell time in minutes
    r = compute_reward_for_dwell_time(df, sample_dwell, alpha=1.0, beta=0.5, gamma=0.2)
    print(f"Reward for {sample_dwell} minutes dwell time: {r:.3f}")