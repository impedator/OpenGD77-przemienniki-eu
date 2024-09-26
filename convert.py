import requests
import csv
import yaml
from geopy.distance import geodesic

# Load configuration from the YAML file
with open("convert.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

country = config['Country']
query_params = config['QueryParams']
zones = config['Zones']

# Base URL for querying przemienniki.eu
base_url = "https://przemienniki.eu/eksport-danych/json/"

# Set the User-Agent to simulate a real browser (latest Firefox)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0'
}

# Prepare to store the channels for later use in zones.csv
channels = []

# Open channels.csv for writing with the new format
with open("Channels.csv", mode="w", newline="") as channels_csv:
    channels_writer = csv.writer(channels_csv, delimiter=';')
    # Write header for channels.csv (your requested format)
    channels_writer.writerow([
        "Channel Number", "Channel Name", "Channel Type", "Rx Frequency", "Tx Frequency", 
        "Bandwidth (kHz)", "Colour Code", "Timeslot", "Contact", "TG List", "DMR ID", 
        "TS1_TA_Tx ID", "TS2_TA_Tx ID", "RX Tone", "TX Tone", "Squelch", "Power", "Rx Only", 
        "Zone Skip", "All Skip", "TOT", "VOX", "No Beep", "No Eco", "APRS", "Latitude", "Longitude"
    ])

    channel_number = 1  # Starting channel number

    # Helper function to replace dots with commas in numerical strings
    def format_number(value):
        return str(value).replace('.', ',') if isinstance(value, (float, int)) else value

    # Loop through each zone and query przemienniki.eu for repeaters
    for zone_name, zone_info in zones.items():
        zone_lat = zone_info['Latitude']
        zone_lon = zone_info['Longitude']
        max_distance = zone_info['MaxDistance']

        # Construct the URL with coordinates and max distance (without prefix)
        url = (f"{base_url}?band={query_params.get('Band', '70cm')}&status={query_params.get('Status', 'working')}"
               f"&coordinates={zone_lat},{zone_lon}&distance={max_distance}")

        print(f"Querying {zone_name} with URL: {url}")
        
        # Fetch data for the current zone with headers (User-Agent)
        response = requests.get(url, headers=headers)

        # Check if the response was successful
        if response.status_code == 200:
            try:
                # Attempt to parse the response as JSON
                repeaters = response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"Error: Unable to parse the response as JSON for {zone_name}.")
                print("Response content:", response.text)
                continue
        else:
            print(f"Error: Failed to fetch data for {zone_name}. Status code: {response.status_code}")
            print("Response content:", response.text)
            continue

        # Process repeaters and add them to the channels.csv
        for repeater in repeaters:
            # Extract latitude and longitude from the coordinates array
            coordinates = repeater.get("coordinates", [None, None])
            repeater_lat = coordinates[0]  # First element is latitude
            repeater_lon = coordinates[1]  # Second element is longitude
            
            receive_freq = format_number(repeater.get("rx_frequency", ""))  # Correct field name and replace dot with comma
            transmit_freq = format_number(repeater.get("tx_frequency", ""))  # Correct field name and replace dot with comma
            callsign = repeater.get("callsign", "")
            modes = repeater.get("modes", [])  # Fetch the list of modes from JSON
            rx_ctcss = repeater.get("rx_ctcss", "")
            tx_ctcss = repeater.get("tx_ctcss", "")
            
            # Process each mode and create a separate channel
            for mode in modes:
                if mode == "dmr":
                    # Create Digital channel
                    channel_type = "Digital"
                    channel_name = f"{callsign}-Digi"
                    bandwidth = ""
                    colour_code = callsign[2] if len(callsign) > 2 else ""
                    timeslot = "1"
                    rx_tone = ""
                    tx_tone = ""
                elif mode == "fm":
                    # Create Analogue channel
                    channel_type = "Analogue"
                    channel_name = f"{callsign}-{mode.upper()}"
                    bandwidth = "12,5"
                    colour_code = ""
                    timeslot = ""
                    rx_tone = rx_ctcss if rx_ctcss not in [False, "false", ""] else ""
                    tx_tone = tx_ctcss if tx_ctcss not in [False, "false", ""] else ""
                else:
                    continue

                # Default values for specific columns
                power = "Master"      # Placeholder for 'Power' 
                rx_only = "No"        # Placeholder for 'Rx Only'
                zone_skip = "No"      # Placeholder for 'Zone Skip'
                all_skip = "No"       # Placeholder for 'All Skip'
                tot = "60"            # Placeholder for 'TOT'
                vox = "No"            # Placeholder for 'VOX'
                no_beep = "No"        # Placeholder for 'No Beep'
                no_eco = "No"         # Placeholder for 'No Eco'
                aprs = "No"           # Placeholder for 'APRS'
                
                # Write the data to channels.csv
                channels_writer.writerow([
                    channel_number, channel_name, channel_type, receive_freq, transmit_freq, 
                    bandwidth, colour_code, timeslot, "", "", "", "", "", 
                    format_number(rx_tone), format_number(tx_tone), "", power, rx_only, 
                    zone_skip, all_skip, tot, vox, no_beep, no_eco, aprs, 
                    format_number(repeater_lat), format_number(repeater_lon)  # Format lat and lon
                ])
                
                # Add to channel list for use in zones.csv
                channels.append({
                    "ZoneName": zone_name,
                    "Channel Name": channel_name,
                    "Channel Type": channel_type,
                    "Channel Number": channel_number
                })

                channel_number += 1  # Increment channel number for each mode

print("Channels.csv has been generated successfully.")

# Open zones.csv for writing
with open("Zones.csv", mode="w", newline="") as zones_csv:
    zones_writer = csv.writer(zones_csv, delimiter=';')

    # Write the header (Zone Name; Channel1; Channel2; ... Channel77)
    header = ["Zone Name"] + [f"Channel{i}" for i in range(1, 78)]
    zones_writer.writerow(header)

    # Process each zone from the YAML configuration
    for zone_name, zone_info in zones.items():
        # Separate channels into Digital and Analogue
        digital_channels = [ch['Channel Name'] for ch in channels if ch['ZoneName'] == zone_name and ch['Channel Type'] == 'Digital']
        analogue_channels = [ch['Channel Name'] for ch in channels if ch['ZoneName'] == zone_name and ch['Channel Type'] == 'Analogue']

        # Create Digital Zone (e.g., Krakow-DIGI)
        digital_zone_name = f"{zone_name}-DIGI"
        digital_row = [digital_zone_name] + digital_channels[:77]  # Max 77 channels
        zones_writer.writerow(digital_row)

        # Create Analogue Zone (e.g., Krakow-FM)
        analogue_zone_name = f"{zone_name}-FM"
        analogue_row = [analogue_zone_name] + analogue_channels[:77]  # Max 77 channels
        zones_writer.writerow(analogue_row)

print("Zones.csv has been generated successfully.")
