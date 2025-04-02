import numpy as np
import pandas as pd

def compute_reward_for_dwell_time(df, dwell_time, alpha=1.0, beta=1.0, gamma=1.0, session_gap=60, threshold=5, extra_penalty_factor=2.0, bonus_factor=0.5):
    dwell_time_seconds = dwell_time * 60
    filtered_df = df[df['TimeSinceStart'] <= dwell_time_seconds]
    
    unique_ips = filtered_df['SrcIP'].unique()
    weighted_unique_ips = 0.0
    for ip in unique_ips:
        ip_records = filtered_df[filtered_df['SrcIP'] == ip]
        scores = ip_records.apply(compute_attack_score, axis=1)
        max_score = scores.max()
        weighted_unique_ips += max_score
    
    weighted_session_count = 0.0
    grouped = filtered_df.groupby('SrcIP')
    for src, group in grouped:
        group = group.sort_values('TimeSinceStart')
        sessions = []
        current_session_scores = []
        last_time = None
        for idx, t in group['TimeSinceStart'].items():
            score = compute_attack_score(group.loc[idx])
            if last_time is None:
                current_session_scores.append(score)
                last_time = t
            else:
                if t - last_time > session_gap:
                    sessions.append(max(current_session_scores))
                    current_session_scores = [score]
                else:
                    current_session_scores.append(score)
                last_time = t
        if current_session_scores:
            sessions.append(max(current_session_scores))
        weighted_session_count += sum(sessions)

    #base_penalty = 2 * np.log(1 + dwell_time)
    base_penalty = (dwell_time_seconds / 60) * 2
    if dwell_time < threshold:
        extra_penalty = (threshold - dwell_time) * extra_penalty_factor
        sustained_bonus = 0
    else:
        first_half = filtered_df[filtered_df['TimeSinceStart'] <= threshold * 60]
        second_half = filtered_df[filtered_df['TimeSinceStart'] > threshold * 60]
        sustained_bonus = bonus_factor * (len(second_half) / len(first_half)) if len(first_half) > 0 else 0
        extra_penalty = 0

    duration_penalty = base_penalty + extra_penalty
    
    reward = alpha * weighted_unique_ips + beta * weighted_session_count + sustained_bonus - gamma * duration_penalty
    return reward

def compute_attack_score(row):
    suspicious_ports = {
        22: 1.5,    # SSH
        23: 1.5,    # Telnet
        3389: 2.0,  # RDP
        80: 1.2,    # HTTP
        443: 1.2,   # HTTPS
        25: 1.5,    # SMTP
        3306: 1.5,  # MySQL
        21: 1.3,    # FTP
        445: 2.0    # SMB
    }
    
    suspicious_countries = {'CN', 'RU', 'IR', 'KP'}
    
    suspicious_asns = {12345, 67890}  # (THIS SHOULD PROBABLY BE DYNAMICALLY UPDATED)
    
    score = 1.0
    
    try:
        port = int(row.get('DstPort', 0))
        score *= suspicious_ports.get(port, 1.0)
    except (ValueError, TypeError):
        pass
    
    src_country = row.get('SrcCountry', '').upper()
    if src_country in suspicious_countries:
        score *= 1.3
    
    try:
        src_asn = int(row.get('SrcASN', 0))
        if src_asn in suspicious_asns:
            score *= 1.4
    except (ValueError, TypeError):
        pass
    
    return score

if __name__ == '__main__':
    from data.data_parser import parse_tcp_syn_data
    df = parse_tcp_syn_data('data/Bitwarden Data Mar 18 2025.json')
    sample_dwell = 10
    r = compute_reward_for_dwell_time(df, sample_dwell, alpha=1.0, beta=0.5, gamma=0.2)
    print(f"Reward for {sample_dwell} minutes dwell time: {r:.3f}")