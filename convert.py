import requests
import csv
import yaml
import xml.etree.ElementTree as ET  # For parsing XML data (przemienniki.net)
from geopy.distance import geodesic

# Load configuration from the YAML file
with open("convert.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

country = config['Country']
data_source = config['DataSource']
query_params = config['QueryParams']
zones = config['Zones']

# Helper function to format numbers
def format_number(value):
    return str(value).replace('.', ',') if isinstance(value, (float, int)) else value

# Prepare to store the channels for later use in zones.csv
channels = []

# Function to handle przemienniki.eu (JSON data)
def fetch_from_przemienniki_eu(zone_name, zone_info):
    zone_lat = zone_info['Latitude']
    zone_lon = zone_info['Longitude']
    max_distance = zone_info['MaxDistance']
    
    url = (f"https://przemienniki.eu/eksport-danych/json/"
           f"?band={query_params['przemienniki.eu']['Band']}"
           f"&mode={query_params['przemienniki.eu']['Mode']}"
           f"&status={query_params['przemienniki.eu']['Status']}"
           f"&coordinates={zone_lat},{zone_lon}&distance={max_distance}")
    
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()  # Return JSON data for processing
        except ValueError:
            print(f"Error: Could not parse JSON for zone {zone_name}.")
            return []
    else:
        print(f"Error: Failed to fetch data from przemienniki.eu for {zone_name}.")
        return []

# Function to handle przemienniki.net (XML data)
def fetch_from_przemienniki_net(zone_name, zone_info):
    zone_lat = zone_info['Latitude']
    zone_lon = zone_info['Longitude']
    max_distance = zone_info['MaxDistance']
    
    url = (f"https://przemienniki.net/export/rxf.xml"
           f"?latitude={zone_lat}&longitude={zone_lon}&range={max_distance}"
           f"&mode={query_params['przemienniki.net']['Mode']}")
    
    response = requests.get(url)
    if response.status_code == 200:
        try:
            # Parse the XML response
            tree = ET.ElementTree(ET.fromstring(response.content))
            return tree  # Return parsed XML tree
        except ET.ParseError:
            print(f"Error: Could not parse XML for zone {zone_name}.")
            return None
    else:
        print(f"Error: Failed to fetch data from przemienniki.net for {zone_name}.")
        return None

# Open channels.csv for writing
with open("channels.csv", mode="w", newline="") as channels_csv:
    channels_writer = csv.writer(channels_csv, delimiter=';')
    channels_writer.writerow([
        "Channel Number", "Channel Name", "Channel Type", "Rx Frequency", "Tx Frequency",
        "Bandwidth (kHz)", "Colour Code", "Timeslot", "Contact", "TG List", "DMR ID", 
        "TS1_TA_Tx ID", "TS2_TA_Tx ID", "RX Tone", "TX Tone", "Squelch", "Power", 
        "Rx Only", "Zone Skip", "All Skip", "TOT", "VOX", "No Beep", "No Eco", "APRS",
        "Latitude", "Longitude"
    ])

    channel_number = 1  # Initialize channel number

    # Loop through zones and fetch data from the appropriate source
    for zone_name, zone_info in zones.items():
        if data_source == "przemienniki.eu":
            repeaters = fetch_from_przemienniki_eu(zone_name, zone_info)
        elif data_source == "przemienniki.net":
            xml_tree = fetch_from_przemienniki_net(zone_name, zone_info)
            if xml_tree is not None:
                repeaters = []
                # Parse XML structure for przemienniki.net
                for repeater in xml_tree.findall('.//repeater'):
                    modes = repeater.find('mode').text.split(',')
                    callsign = repeater.find('qra').text
                    # rx_freq = format_number(repeater.find('rx').text)
                    # tx_freq = format_number(repeater.find('tx').text)
                    lat = repeater.find('location/latitude').text
                    lon = repeater.find('location/longitude').text

                    rx_freq = ""
                    tx_freq = ""
                    for qrg in repeater.findall('qrg'):
                        if qrg.attrib['type'] == 'rx':
                            rx_freq = format_number(qrg.text)
                        elif qrg.attrib['type'] == 'tx':
                            tx_freq = format_number(qrg.text)
                    repeaters.append({
                        "callsign": callsign,
                        "rx_frequency": rx_freq,
                        "tx_frequency": tx_freq,
                        "modes": modes,
                        "latitude": lat,
                        "longitude": lon
                    })
            else:
                repeaters = []
        else:
            print(f"Unsupported data source: {data_source}")
            continue

        # Process each repeater for channels.csv
        for repeater in repeaters:
            for mode in repeater['modes']:
                if mode.lower() == "dmr" or mode.lower() == "mototrbo":
                    channel_type = "Digital"
                    channel_name = f"{repeater['callsign']}-Digi"
                    timeslot = "1"
                    colour_code = repeater['callsign'][2] if len(repeater['callsign']) > 2 else ""
                elif mode.lower() == "fm":
                    channel_type = "Analogue"
                    channel_name = f"{repeater['callsign']}-FM"
                    timeslot = ""
                    colour_code = ""
                else:
                    continue  # Skip unsupported modes
                
                # Write to channels.csv
                channels_writer.writerow([
                    channel_number, channel_name, channel_type, repeater['rx_frequency'], 
                    repeater['tx_frequency'], "", colour_code, timeslot, "", "", "", "", "", 
                    "", "", "", "Master", "No", "No", "No", "60", "No", "No", "No", 
                    format_number(repeater['latitude']), format_number(repeater['longitude'])
                ])
                
                # Add to list for zones.csv
                channels.append({
                    "ZoneName": zone_name,
                    "Channel Name": channel_name,
                    "Channel Type": channel_type,
                    "Channel Number": channel_number
                })
                channel_number += 1

print("channels.csv has been generated successfully.")

# Generate zones.csv
with open("zones.csv", mode="w", newline="") as zones_csv:
    zones_writer = csv.writer(zones_csv, delimiter=';')
    header = ["Zone Name"] + [f"Channel{i}" for i in range(1, 78)]
    zones_writer.writerow(header)

    for zone_name in zones:
        digital_channels = [ch['Channel Name'] for ch in channels if ch['ZoneName'] == zone_name and ch['Channel Type'] == 'Digital']
        analogue_channels = [ch['Channel Name'] for ch in channels if ch['ZoneName'] == zone_name and ch['Channel Type'] == 'Analogue']

        # Digital Zone (e.g., Krakow-DIGI)
        digital_row = [f"{zone_name}-DIGI"] + digital_channels[:77]
        zones_writer.writerow(digital_row)

        # Analogue Zone (e.g., Krakow-FM)
        analogue_row = [f"{zone_name}-FM"] + analogue_channels[:77]
        zones_writer.writerow(analogue_row)

print("zones.csv has been generated successfully.")
