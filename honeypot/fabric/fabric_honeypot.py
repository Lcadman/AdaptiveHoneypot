from honeypot.fabric import (
    config,
)  # This file sets the environment variables for connecting to Fabric.
from fabrictestbed_extensions.fablib.fablib import FablibManager
from time import sleep
from tqdm import tqdm
from yaspin import yaspin
import random
import socket

DWELL_TIME_SECONDS = 300
USER_DATA = "bash /local/repository/cloud_init.sh"
LOCAL_PATH = "/Users/lcadman/Documents/School/Research/AdaptiveHoneypot/honeypot/fabric/cloud_init.yaml"


def launch_slice_with_fablib():
    fablib = FablibManager()
    sites_to_try = ["TACC", "WASH", "UTAH", "MAX"]

    try:
        with yaspin(
            text="Creating slice and submitting to FABRIC...", color="cyan"
        ) as spinner:
            slice = fablib.new_slice(name="honeypot_slice")
            node = None
            random.shuffle(sites_to_try)
            for site in sites_to_try:
                try:
                    node = slice.add_node(name="honeypot_node", site=site)
                    print(f"Successfully added node at site: {site}")
                    break
                except Exception as site_error:
                    print(f"Failed to add node at site {site}: {site_error}")
            if not node:
                raise RuntimeError("Failed to add node at all attempted sites.")

            slice.submit(wait=True)
            spinner.ok("✅ ")

        print(f"Slice '{slice.get_name()}' is active!")

        return slice
    except Exception as e:
        print("Error launching slice with fablib:", e)
        return None


def start_remote_honeypot(node):
    try:
        print("Starting remote honeypot...")
        command = "docker run -d --name glutton --net=host -v /local/honeypot:/data mohammadne/glutton"
        stdout, stderr = node.execute(command)
        print("Remote honeypot start output:")
        print(stdout)
        if stderr:
            print("Errors:")
            print(stderr)
    except Exception as e:
        print("Error starting remote honeypot:", e)


def stop_remote_honeypot(node):
    try:
        print("Stopping remote honeypot...")
        command = "docker stop glutton && docker rm glutton"
        stdout, stderr = node.execute(command)
        print("Remote honeypot stop output:")
        print(stdout)
        if stderr:
            print("Errors:")
            print(stderr)
    except Exception as e:
        print("Error stopping remote honeypot:", e)


def excecute_startup_script(node):
    try:
        print("Executing startup script...")
        setup_commands = [
            "dnf update -y",
            "dnf install -y docker wget",
            "systemctl start docker && systemctl enable docker",
            "mkdir -p /local/honeypot && wget -O /local/honeypot/local_honeypot.py https://yourserver.com/path/to/local_honeypot.py",
        ]

        stdout, stderr = node.execute(setup_commands)

        if stdout:
            print("STDOUT:")
            print(stdout)

        if stderr:
            print("STDERR:")
            print(stderr)

        if "error" in stderr.lower() or "failed" in stderr.lower():
            print("⚠️  Command(s) might have failed!")
        print("Startup script output:")
        print(stdout)
        if stderr:
            print("Errors:")
            print(stderr)
    except Exception as e:
        print("Error executing startup script:", e)


def retrieve_data_from_honeypot(node):
    try:
        print("Retrieving data file from honeypot node...")
        remote_path = "/local/honeypot/output.log"
        local_path = "/Users/lcadman/Documents/Research/data/output.log"
        node.download_file(remote_path, local_path)
        print(f"Data downloaded to {local_path}")
    except Exception as e:
        print("Error downloading file from honeypot:", e)


def main():
    slice_obj = launch_slice_with_fablib()

    if not slice_obj:
        print("Failed to launch slice.")
        return

    print("Slice launched and is active.")

    # Retrieve the node from the slice
    node = slice_obj.get_node("honeypot_node")

    # Get SSH command for debugging
    node = slice_obj.get_node("honeypot_node")
    ssh_command = node.get_ssh_command()
    print(f"SSH into your node using the following command:\n{ssh_command}")

    # Execute the startup script on the node
    excecute_startup_script(node)
    if not node:
        print("Failed to execute startup script.")
        return
    print("Startup script executed successfully.")

    # Start the honeypot remotely
    start_remote_honeypot(node)
    print(f"Remote honeypot running for {DWELL_TIME_SECONDS} seconds...")
    for _ in tqdm(range(DWELL_TIME_SECONDS), desc="Honeypot active time"):
        sleep(1)

    # Stop the honeypot
    stop_remote_honeypot(node)

    retrieve_data_from_honeypot()

    print(
        "Honeypot session complete. Ready for controller to retrieve data, if applicable."
    )


if __name__ == "__main__":
    main()
