import pandas as pd

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

    return state