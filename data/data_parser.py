import json
import pandas as pd


def parse_tcp_syn_data(filename):
    records = []
    with open(filename, "r") as file:
        for line in file:
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"Error decoding line: {line}\nError: {e}")
    # Convert list of records to a DataFrame
    df = pd.DataFrame(records)
    # Convert 'TimeSinceStart' to numeric (in seconds)
    df["TimeSinceStart"] = pd.to_numeric(df["TimeSinceStart"], errors="coerce")
    # Optionally, convert the 'Time' field to datetime if needed:
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    return df


# Simple test code
if __name__ == "__main__":
    df = parse_tcp_syn_data("../data/Bitwarden Data Mar 18 2025.json")
    print("Data head:")
    print(df.head())
    print("Data info:")
    print(df.info())
