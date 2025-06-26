from bandit.rl_agent import SimpleQAgent
from controller.controller import run_controller_session
import numpy as np
import time
import pickle
import os
from collections import defaultdict

AGENT_FILE = "logs/q_agent.pkl"

def main():
    #dwell_times = np.linspace(0, 25, 20).tolist()
    dwell_times = [0, 5, 10, 15, 20, 25, 30, 45, 60]

    if os.path.exists(AGENT_FILE):
        with open(AGENT_FILE, "rb") as f:
            agent = pickle.load(f)
        print("✅ Loaded existing agent.")
    else:
        agent = SimpleQAgent(dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1)
        print("🆕 Created new agent.")

    total_runs = 50  # You can modify this for testing or continuous operation
    log_path = "logs/main_run_log.txt"
    os.makedirs("logs", exist_ok=True)

    for i in range(total_runs):
        print(f"\n🔁 Starting honeypot session {i+1}/{total_runs}")
        run_controller_session(agent)
        with open(AGENT_FILE, "wb") as f:
            pickle.dump(agent, f)
        with open(log_path, "a") as logf:
            logf.write(f"Completed session {i+1} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        time.sleep(10)

    # Print average Q-values by dwell time
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
    main()
