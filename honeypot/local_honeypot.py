import time
import subprocess
import json
import os
import datetime

class LocalHoneypot:
    """
    LocalHoneypot is responsible for:
      - Starting a Cowrie honeypot instance.
      - Running the honeypot for a predetermined dwell time.
      - Stopping the honeypot and aggregating the logs into a JSON file.
    
    The aggregated data will include at least:
      - Start and end timestamps.
      - Total number of connections.
      - Count of unique IP addresses.
      - Connection rate over the dwell time.
    
    The agent controller will later poll for this file.
    """
    
    def __init__(self, dwell_time_minutes, 
                 aggregated_log_file="aggregated_data.json", 
                 cowrie_start_script="./start-cowrie.sh", 
                 cowrie_stop_script="./stop-cowrie.sh", 
                 raw_log_file="cowrie.log"):
        """
        Initialize with:
          dwell_time_minutes: Duration to run the honeypot.
          aggregated_log_file: Destination for the aggregated data.
          cowrie_start_script: Script or command to start Cowrie.
          cowrie_stop_script: Script or command to stop Cowrie.
          raw_log_file: File path to the raw Cowrie log file.
        """
        self.dwell_time_minutes = dwell_time_minutes
        self.aggregated_log_file = aggregated_log_file
        self.cowrie_start_script = cowrie_start_script
        self.cowrie_stop_script = cowrie_stop_script
        self.raw_log_file = raw_log_file
        self.cowrie_process = None

    def start_cowrie(self):
        """Starts the Cowrie honeypot using a subprocess."""
        try:
            print("Starting Cowrie using:", self.cowrie_start_script)
            # Launch the start script (adjust parameters as needed)
            self.cowrie_process = subprocess.Popen([self.cowrie_start_script])
        except Exception as e:
            print("Error starting Cowrie honeypot:", e)

    def stop_cowrie(self):
        """Stops the Cowrie honeypot using a predefined stop script."""
        try:
            if self.cowrie_process:
                print("Stopping Cowrie using:", self.cowrie_stop_script)
                subprocess.run([self.cowrie_stop_script])
                self.cowrie_process.wait()
        except Exception as e:
            print("Error stopping Cowrie honeypot:", e)

    def aggregate_logs(self):
        """
        Aggregates the raw Cowrie logs into a JSON file.
        This function simulates aggregation by:
          - Counting the total number of connections (i.e., log lines).
          - Determining the unique IPs (assuming each log line starts with the IP).
          - Calculating a connection rate (connections per second).
        
        You can extend this to extract additional information from the raw logs.
        """
        log_lines = []
        if os.path.exists(self.raw_log_file):
            try:
                with open(self.raw_log_file, "r") as f:
                    log_lines = f.readlines()
            except Exception as e:
                print("Error reading raw log file:", e)
        else:
            print("Raw log file not found:", self.raw_log_file)
        
        # Extract information from logs (this is a simplified example)
        total_connections = len(log_lines)
        # Assume each line's first token is an IP address
        unique_ips = set()
        for line in log_lines:
            if line.strip():
                tokens = line.split()
                if tokens:
                    unique_ips.add(tokens[0])
        
        # Calculate the connection rate (connections per second)
        dwell_time_seconds = self.dwell_time_minutes * 60
        connection_rate = total_connections / dwell_time_seconds if dwell_time_seconds > 0 else 0
        
        # For demonstration, mark start and end times based on current time
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=self.dwell_time_minutes)
        
        aggregated_data = {
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "total_connections": total_connections,
            "unique_ips": len(unique_ips),
            "connection_rate": connection_rate
            # Add more detailed fields here as needed.
        }
        
        # Save aggregated data
        try:
            with open(self.aggregated_log_file, "w") as f:
                json.dump(aggregated_data, f, indent=4)
            print("Aggregated data saved to", self.aggregated_log_file)
        except Exception as e:
            print("Error writing aggregated data file:", e)
        
        return aggregated_data

    def run(self):
        """Run the complete honeypot lifecycle:
           - Start Cowrie
           - Wait for the dwell time
           - Stop Cowrie and aggregate logs
        """
        print("Initializing honeypot run...")
        self.start_cowrie()
        print(f"Cowrie honeypot running for {self.dwell_time_minutes} minutes...")
        time.sleep(self.dwell_time_minutes * 60)  # Wait for the specified dwell time
        print("Dwell time completed. Stopping honeypot...")
        self.stop_cowrie()
        print("Aggregating logs...")
        aggregated_data = self.aggregate_logs()
        print("Honeypot session complete.")
        return aggregated_data

if __name__ == "__main__":
    # Example usage - adjust dwell time and file paths as needed
    dwell_time = 10  # minutes
    honeypot = LocalHoneypot(
        dwell_time_minutes=dwell_time,
        aggregated_log_file="aggregated_data.json",
        cowrie_start_script="./start-cowrie.sh",  # Replace with actual script path
        cowrie_stop_script="./stop-cowrie.sh",    # Replace with actual script path
        raw_log_file="cowrie.log"                 # Replace with the actual log file location
    )
    aggregated_data = honeypot.run()
    print("Aggregated Data:", aggregated_data)