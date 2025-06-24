import subprocess
from time import sleep
from tqdm import tqdm
from yaspin import yaspin

# Config Constants
INSTANCE_NAME = "honeypot-instance"
ZONE = "us-central1-a"
MACHINE_TYPE = "e2-medium"
IMAGE_FAMILY = "debian-11"
IMAGE_PROJECT = "debian-cloud"
REMOTE_OUTPUT_LOG = "/home/lcadman/honeypot/data/tcpdump_output.log"
LOCAL_OUTPUT_LOG = "/Users/lcadman/Documents/School/Research/AdaptiveHoneypot/tcpdump_output.log"
DWELL_TIME_SECONDS = 300

def launch_instance():
    try:
        with yaspin(text="Creating GCP instance...", color="cyan") as spinner:
            subprocess.run([
                "gcloud", "compute", "instances", "create", INSTANCE_NAME,
                "--zone", ZONE,
                "--machine-type", MACHINE_TYPE,
                "--image-family", IMAGE_FAMILY,
                "--image-project", IMAGE_PROJECT,
                "--tags", "http-server,https-server",
                "--quiet"
            ], check=True)
            spinner.ok("✅ ")
        print("Instance launched and booting up.")
    except subprocess.CalledProcessError as e:
        print("Error creating GCP instance:", e)
        exit(1)

def get_instance_ip():
    try:
        result = subprocess.run([
            "gcloud", "compute", "instances", "describe", INSTANCE_NAME,
            "--zone", ZONE,
            "--format=get(networkInterfaces[0].accessConfigs[0].natIP)"
        ], capture_output=True, text=True, check=True)
        ip_address = result.stdout.strip()
        print(f"Public IP address of instance: {ip_address}")
        return ip_address
    except subprocess.CalledProcessError as e:
        print("Failed to get instance IP:", e)
        return None

def ensure_firewall_rule():
    rule_name = "honeypot-allow"
    try:
        result = subprocess.run([
            "gcloud", "compute", "firewall-rules", "describe", rule_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Firewall rule '{rule_name}' not found. Creating it...")
        try:
            subprocess.run([
                "gcloud", "compute", "firewall-rules", "create", rule_name,
                "--allow", "tcp:1-65535",
                "--target-tags", "honeypot",
                "--source-ranges", "0.0.0.0/0",
                "--description", "Allow all TCP ports for honeypot"
            ], check=True)
            print(f"Firewall rule '{rule_name}' created.")
        except subprocess.CalledProcessError as e:
            print("Failed to create firewall rule:", e)

def tag_instance_for_firewall():
    try:
        subprocess.run([
            "gcloud", "compute", "instances", "add-tags", INSTANCE_NAME,
            "--zone", ZONE,
            "--tags", "honeypot"
        ], check=True)
        print("Tag 'honeypot' applied to instance.")
    except subprocess.CalledProcessError as e:
        print("Failed to tag instance for firewall rule:", e)

def run_command_on_instance(command):
    try:
        result = subprocess.run([
            "gcloud", "compute", "ssh", INSTANCE_NAME,
            "--zone", ZONE,
            "--command", command,
            "--quiet"
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Command failed:", e)

def setup_instance():
    commands = [
        "sudo apt-get update -y",
        "sudo apt-get install -y tcpdump",
        "mkdir -p ~/honeypot"
    ]
    print("Setting up instance...")
    for i in tqdm(range(3), desc="Setup steps"):
        run_command_on_instance(commands[i])
        sleep(1)

def start_honeypot():
    command = (
        "nohup sudo tcpdump -tttt -i any "
        "'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0' "
        "> ~/honeypot/tcpdump_output.log 2>&1 &"
    )
    try:
        with yaspin(text="Starting honeypot...", color="magenta") as spinner:
            run_command_on_instance(command)
            spinner.ok("✅ ")
    except Exception as e:
        print("Failed to start honeypot:", e)

def stop_honeypot():
    with yaspin(text="Stopping honeypot...", color="yellow") as spinner:
        run_command_on_instance("sudo pkill tcpdump")
        spinner.ok("✅ ")

def download_logs():
    try:
        with yaspin(text="Downloading logs...", color="blue") as spinner:
            subprocess.run([
                "gcloud", "compute", "scp",
                f"{INSTANCE_NAME}:/home/lcadman/honeypot/data/tcpdump_output.log",
                LOCAL_OUTPUT_LOG,
                "--zone", ZONE,
                "--quiet"
            ], check=True)
            spinner.ok("✅ ")
            print(f"Logs saved to {LOCAL_OUTPUT_LOG}")
    except subprocess.CalledProcessError as e:
        print("Failed to download log file:", e)

def delete_instance():
    try:
        with yaspin(text="Deleting instance...", color="red") as spinner:
            subprocess.run([
                "gcloud", "compute", "instances", "delete", INSTANCE_NAME,
                "--zone", ZONE,
                "--quiet"
            ], check=True)
            spinner.ok("✅ ")
            print("Instance deleted.")
    except subprocess.CalledProcessError as e:
        print("Failed to delete instance:", e)

def main():
    launch_instance()
    ensure_firewall_rule()
    tag_instance_for_firewall()
    print("Waiting for instance to initialize...")
    for _ in tqdm(range(60), desc="Instance boot"):
        sleep(1)

    ip = get_instance_ip()
    setup_instance()
    start_honeypot()

    print(f"Honeypot running for {DWELL_TIME_SECONDS} seconds...")
    for _ in tqdm(range(DWELL_TIME_SECONDS), desc="Dwell time"):
        sleep(1)

    stop_honeypot()
    download_logs()
    delete_instance()

    print("Session complete.")

if __name__ == "__main__":
    main()