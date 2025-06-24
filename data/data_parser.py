import json
import pandas as pd
import re
from datetime import datetime
import ipaddress
import geoip2.database


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


def parse_tcpdump_log(filename, output_json_path=None, geoip_path=None):
    # Appends parsed records to output_json_path instead of overwriting
    records = []
    start_time = None
    asn_reader = None
    city_reader = None

    if geoip_path:
        try:
            asn_reader = geoip2.database.Reader(f"{geoip_path}/GeoLite2-ASN.mmdb")
            city_reader = geoip2.database.Reader(f"{geoip_path}/GeoLite2-Country.mmdb")
        except Exception as e:
            print(f"Error loading GeoIP databases: {e}")

    with open(filename, "r") as file:
        for line in file:
            match = re.match(
                r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+\S+\s+In\s+IP\s+(?P<src>[\w\.\-]+)\.(?P<src_port>\d+)\s+>\s+(?P<dst>[\w\.\-]+)\.(?P<dst_port>\d+):.*",
                line
            )
            if match:
                t = datetime.strptime(match.group("time"), "%Y-%m-%d %H:%M:%S.%f")
                if not start_time:
                    start_time = t
                src_ip = match.group("src")
                try:
                    ipaddress.ip_address(src_ip)
                except ValueError:
                    continue  # skip hostnames

                src_asn = None
                src_country = None
                if asn_reader and city_reader:
                    try:
                        asn_resp = asn_reader.asn(src_ip)
                        src_asn = asn_resp.autonomous_system_number
                        country_resp = city_reader.country(src_ip)
                        src_country = country_resp.country.iso_code
                    except:
                        pass

                record = {
                    "Time": t.isoformat() + "Z",
                    "TimeSinceStart": (t - start_time).total_seconds(),
                    "SrcIP": src_ip,
                    "SrcPort": int(match.group("src_port")),
                    "DstIP": match.group("dst"),
                    "DstPort": int(match.group("dst_port")),
                    "SrcASN": src_asn,
                    "SrcCountry": src_country
                }
                records.append(record)

    if output_json_path:
        with open(output_json_path, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    return pd.DataFrame(records)


# Simple test code
if __name__ == "__main__":
    print("\nParsed TCPDump Log:")
    df_parsed = parse_tcpdump_log(
        "/Users/lcadman/Documents/School/Research/AdaptiveHoneypot/data/tcpdump_output.log",
        output_json_path="/Users/lcadman/Documents/School/Research/AdaptiveHoneypot/data/tcpdump_output.json",
        geoip_path="/Users/lcadman/Documents/School/Research/AdaptiveHoneypot/geoip"
    )
    print(df_parsed.head())
