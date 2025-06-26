# analyze_q_values.py

import pickle
from collections import defaultdict

AGENT_FILE = "logs/q_agent.pkl"

def load_agent():
    with open(AGENT_FILE, "rb") as f:
        return pickle.load(f)

def analyze_q_values(agent):
    dwell_q_values = defaultdict(list)

    for actions in agent.q_table.values():
        for dwell_time, q_value in actions.items():
            dwell_q_values[dwell_time].append(q_value)

    avg_q = {dt: sum(vals) / len(vals) for dt, vals in dwell_q_values.items()}
    sorted_avg_q = sorted(avg_q.items(), key=lambda x: x[1], reverse=True)

    print("\n📊 Average Q-values by dwell time:")
    for dt, q in sorted_avg_q:
        print(f"  Dwell Time: {dt} min → Avg Q-value: {q:.2f}")

if __name__ == "__main__":
    agent = load_agent()
    analyze_q_values(agent)