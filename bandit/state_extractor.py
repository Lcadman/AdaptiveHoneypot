import pandas as pd
import numpy as np

def extract_state(df):
    state = {}
    state['total_connections'] = len(df)
    state['unique_ips'] = df['SrcIP'].nunique()
    
    if len(df) > 1:
        state['avg_time_gap'] = df['TimeSinceStart'].diff().dropna().mean()
    else:
        state['avg_time_gap'] = 0.0
        
    session_gap = 60
    session_count = 0
    if len(df) > 0:
        sorted_times = df['TimeSinceStart'].sort_values().values
        session_count = 1
        for i in range(1, len(sorted_times)):
            if sorted_times[i] - sorted_times[i-1] > session_gap:
                session_count += 1
    state['session_count'] = session_count

    if len(df) > 0:
        total_time = df['TimeSinceStart'].max() - df['TimeSinceStart'].min()
        if total_time > 0:
            state['connection_rate'] = state['total_connections'] / total_time
        else:
            state['connection_rate'] = 0.0
    else:
        state['connection_rate'] = 0.0

    if len(df) > 1:
        sorted_df = df.sort_values('TimeSinceStart')
        times = sorted_df['TimeSinceStart'].values
        cumulative_connections = np.arange(1, len(times) + 1)
        slope = np.polyfit(times, cumulative_connections, 1)
        state['traffic_trend'] = slope
    else:
        state['traffic_trend'] = 0.0

    if len(df) > 0:
        median_time = df['TimeSinceStart'].median()
        first_half = df[df['TimeSinceStart'] <= median_time]
        second_half = df[df['TimeSinceStart'] > median_time]
        if len(first_half) > 0:
            sustainability = len(second_half) / len(first_half)
        else:
            sustainability = 0.0
        state['attack_sustainability'] = sustainability
    else:
        state['attack_sustainability'] = 0.0

    return state

# For testing
if __name__ == '__main__':
    from data.data_parser import parse_tcp_syn_data
    df = parse_tcp_syn_data('../data/Bitwarden Data Mar 18 2025.json')
    state = extract_state(df)
    print("Extracted state:", state)