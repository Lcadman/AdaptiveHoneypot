from bandit.rl_agent import SimpleQAgent
from controller.controller import run_controller_session
import numpy as np
import time
import pickle
import os

AGENT_FILE = "logs/q_agent.pkl"

def main():
    dwell_times = np.linspace(5, 15, 21).tolist()
    
    if os.path.exists(AGENT_FILE):
        with open(AGENT_FILE, "rb") as f:
            agent = pickle.load(f)
        print("✅ Loaded existing agent.")
    else:
        agent = SimpleQAgent(dwell_times, alpha=0.1, gamma=0.9, epsilon=0.1)
        print("🆕 Created new agent.")

    total_runs = 10  # You can modify this for testing or continuous operation
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

if __name__ == "__main__":
    main()
