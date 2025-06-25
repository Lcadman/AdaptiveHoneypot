import os
import time
import datetime
from honeypot.gcp_honeypot import (
    launch_instance, ensure_firewall_rule, tag_instance_for_firewall,
    setup_instance, start_honeypot, stop_honeypot,
    download_logs, delete_instance
)
from data.data_parser import parse_tcpdump_log
from bandit.reward import compute_reward_for_dwell_time
from bandit.state_extractor import extract_state
from bandit.rl_agent import SimpleQAgent
import json
from tqdm import tqdm

LOG_DIR = "logs"
GEOIP_PATH = "geoip"
LOCAL_LOG_PATH = "tcpdump_output.log"

def convert_state_for_json(state):
    return {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in state.items()}

def run_controller_session(agent: SimpleQAgent):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(LOG_DIR, f"session_{timestamp}.json")
    csv_path = os.path.join(LOG_DIR, "controller_log.csv")

    os.makedirs(LOG_DIR, exist_ok=True)

    if os.path.exists(LOCAL_LOG_PATH):
        df = parse_tcpdump_log(LOCAL_LOG_PATH, geoip_path=GEOIP_PATH)
        if df.empty:
            print("No TCP SYN data collected.")
            return
        state = extract_state(df)
    else:
        print("No previous log found — using initial state.")
        state = {k: 0 for k in ['count', 'unique_src', 'avg_ports']}

    selected_dwell = agent.select_action(state)

    try:
        launch_instance()
        ensure_firewall_rule()
        tag_instance_for_firewall()
        print("Waiting for instance to initialize...")
        for _ in tqdm(range(60), desc="Instance boot"):
            time.sleep(1)
        setup_instance()

        print(f"\nRunning honeypot for {selected_dwell} minutes...")
        start_honeypot()
        print(f"Honeypot running for {selected_dwell * 60} seconds...")
        for _ in tqdm(range(int(selected_dwell * 60)), desc="Dwell time"):
            time.sleep(1)
        stop_honeypot()
        download_logs()
        delete_instance()

        # Parse logs and enrich with GeoIP
        df = parse_tcpdump_log(LOCAL_LOG_PATH, output_json_path=json_path, geoip_path=GEOIP_PATH)
        if df.empty:
            print("No TCP SYN data collected.")
            return

        # Extract new state and reward
        print("Parsed DF head:\n", df.head())
        print("Row count:", len(df))
        print("Unique SrcIP:", df["SrcIP"].nunique())
        print("Unique DstPort:", df["DstPort"].nunique())
        new_state = extract_state(df)
        reward = compute_reward_for_dwell_time(df, selected_dwell)
        agent.update(state, selected_dwell, reward, new_state)

        # Append metadata
        with open(csv_path, "a") as f:
            f.write(json.dumps({
                "timestamp": timestamp,
                "selected_dwell": selected_dwell,
                "reward": reward,
                "state": convert_state_for_json(state),
                "next_state": convert_state_for_json(new_state),
                "json_log": json_path
            }) + "\n")

        print(f"✅ Session {timestamp} complete.")

    except Exception as e:
        print("❌ Error during session:", e)
        try:
            stop_honeypot()
            delete_instance()
        except:
            pass
