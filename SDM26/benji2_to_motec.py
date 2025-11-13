#!/usr/bin/env python3
"""
Convert BENJI2 binary telemetry files directly to MoTeC .ld format
"""
from datetime import datetime
import os
from devices import create_devices, configure_devices


# Channel units mapping for MoTeC conversion
CHANNEL_UNITS = {
    "TS": "s",
    "CURRENT": "A",
    "BATTERY": "V",
    "IMU_X_ACCEL": "g",
    "IMU_Y_ACCEL": "g",
    "IMU_Z_ACCEL": "g",
    "IMU_X_GYRO": "deg/s",
    "IMU_Y_GYRO": "deg/s",
    "IMU_Z_GYRO": "deg/s",
    "FL_SG": "lbs",
    "FR_SG": "lbs",
    "RL_SG": "lbs",
    "RR_SG": "lbs",
    "FLW_AMB": "°C",
    "FRW_AMB": "°C",
    "RLW_AMB": "°C",
    "RRW_AMB": "°C",
    "FLW_RTR": "°C",
    "FRW_RTR": "°C",
    "RLW_RTR": "°C",
    "RRW_RTR": "°C",
}




def parseBenji2File(file_path: str):
    """
    Parse a BENJI2 binary file and return samples, frequency, and device info

    Args:
        file_path: Path to the .benji2 file

    Returns:
        Tuple of (samples, freq, devices)
        - samples: List of sample rows
        - freq: Sampling frequency in Hz
        - devices: List of device_data objects
    """
    with open(file_path, 'br') as f:

        # Get the Length of the Header String
        # Get the Length of the Header String
        data = f.read(4)
        headerLen = int.from_bytes(data, "little", signed=False) - 1


        print(headerLen)


        # Grab the Header String
        data = f.read(headerLen)
        header = data.decode("utf-8")
        filtered_header, dataSize = filter_duplicate_headers(header)

        deviceList = [key.strip() for key in filtered_header.split(",")]
        devices = create_devices(deviceList, dataSize)
        configure_devices(devices)

        

        f.read(1) # Changed from reading 2 bytes to 1 byte, SDM26 Logger Does Not include a null terminator in header

        # # Seek back to read first timestamp as part of data loop
        # data = f.read(devices[0].byte_size)
        # f.seek(-4, os.SEEK_CUR)

        # Store samples in memory
        samples = []

        while data:
            # Parallel Array to the header
            outputList = [None] * len(devices)
            incomplete = False
            for device in devices:
                data = f.read(device.byte_size)
                if not data:
                    incomplete = True
                    break

                outputList[device.column_index] = device.getData(data)

            # Only store complete samples (skip rows with None values)
            if not incomplete and None not in outputList:
                samples.append(outputList)

        # Calculate sampling frequency from timestamp data
        if len(samples) >= 2:
            time_delta = samples[1][0] - samples[0][0]  # TS is first column (index 0)
            freq = int(round(1 / time_delta))  # Round to nearest integer
            print(f"Calculated frequency: {freq} Hz (time delta: {time_delta} s)")
        else:
            freq = 500  # Default fallback if not enough samples
            print(f"Warning: Not enough samples to calculate frequency, using default {freq} Hz")

        print(f"Parsed {len(samples)} samples from benji2 file")
        return samples, freq, devices


def convert_benji2_to_motec(samples, freq, devices, output_path):
    """
    Convert parsed benji2 data to MoTeC .ld format

    Args:
        samples: List of sample rows (each row is a list of values)
        freq: Sampling frequency in Hz
        devices: List of device_data objects with channel info
        output_path: Path to write the .ld file
    """
    from motec_ld import MotecLog, MotecChannel, MotecEvent

    print(f"[DEBUG] Converting to MoTeC: {output_path}")

    # Create MoTeC log
    log = MotecLog()
    now = datetime.now()
    log.date = now.strftime('%d/%m/%Y')
    log.time = now.strftime('%H:%M:%S')
    log.driver = "Driver"
    log.vehicle = "Vehicle"
    log.venue = "Track"
    log.comment = "BENJI2 -> MoTeC conversion"

    # Create event
    log.event = MotecEvent({
        "name": "Session",
        "session": "Run",
        "comment": f"{len(devices)} channels, {len(samples)} samples",
        "venuepos": 0
    })

    # Create channels
    for i, device in enumerate(devices):
        units = CHANNEL_UNITS.get(device.name, "raw")  # Lookup units, default to "raw"
        ch_def = {
            "name": device.name,
            "shortname": device.name[:8],  # Truncate to 8 chars
            "units": units,
            "id": 8000 + i,
            "freq": freq,
            "shift": 0,
            "multiplier": 1,
            "scale": 1,
            "decplaces": 2,
            "datatype": 0x07,  # Float
            "datasize": 4       # 4-byte float
        }
        ch = MotecChannel(ch_def)
        log.add_channel(ch)
        if i < 5 or i % 5 == 0:
            print(f"[DEBUG] Added channel: {device.name} ({units}) (ID {ch.id})")

    # Set time channel
    for ch in log.channels:
        if ch.name == "TS":
            log.time_channel = ch
            print(f"[DEBUG] Time channel set: {ch.name} (ID {ch.id})")
            break

    # Add all samples
    print(f"[DEBUG] Adding {len(samples)} samples...")
    for row_idx, row in enumerate(samples):
        log.add_samples(row)
        if row_idx < 3:
            print(f"[DEBUG] Sample {row_idx}: {row[:5]}...")  # Show first 5 values

    # Write output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(log.to_string())

    print(f"[DEBUG] MoTeC file written: {output_path} ({len(samples)} samples, {len(devices)} channels)")


def filter_duplicate_headers(header_str: str) -> tuple[str, list[int]]:
    """
    Filter CSV header string and count occurrences of each base name

    Args:
        header_str: String containing comma-separated header names

    Returns:
        Tuple containing:
            - Filtered header string with duplicates removed
            - List of integers representing count of each base name

    Example:
        Input: "TS,TS1,TS2,TS3"
        Output: ("TS", [4])
    """
    # Split headers and remove extra whitespace
    headers = [h.strip() for h in header_str.split(',')]
    base_counts = {}
    filtered = []

    for header in headers:
        header = header.strip('\x00')
        base = header.rstrip('0123456789')
        base = base.strip()
        if base not in base_counts:
            filtered.append(base)
            base_counts[base] = 1
        else:
            base_counts[base] += 1

    counts = [base_counts[base] for base in filtered]

    return ','.join(filtered), counts


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    import sys
    import glob
    import time

    if len(sys.argv) < 2:
        print("Usage: python benji2_to_motec.py <directory>")
        print("\nExample:")
        print("  python benji2_to_motec.py data_benji")
        exit(1)

    start_time = time.time()
    directory = sys.argv[1]
    benji2_files = glob.glob(os.path.join(directory, "*.benji2"))

    if not benji2_files:
        print(f"No .benji2 files found in {directory}")
        exit(1)

    # Create processed_motec directory if it doesn't exist
    output_dir = "processed_motec"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    total_files = len(benji2_files)
    print(f"\nFound {total_files} .benji2 files to process")
    print("-" * 50)

    for index, benji2_file in enumerate(benji2_files, 1):
        # Create output file path in processed_motec directory
        output_filename = os.path.basename(os.path.splitext(benji2_file)[0]) + ".ld"
        output_file = os.path.join("processed_motec", output_filename)
        
        # Calculate progress percentage
        progress = (index / total_files) * 100
        print(f"[{progress:3.1f}%] Processing file {index}/{total_files}: {os.path.basename(benji2_file)}")

        try:
            # Parse benji2 file
            samples, freq, devices = parseBenji2File(benji2_file)

            # Convert to MoTeC
            convert_benji2_to_motec(samples, freq, devices, output_file)

            print(f"Successfully converted {os.path.basename(benji2_file)}")
        except Exception as e:
            print(f"Error converting {os.path.basename(benji2_file)}: {str(e)}")
            continue

    end_time = time.time()
    total_time = end_time - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    print(f"\nConversion process complete!")
    print(f"Total processing time: {minutes} minutes and {seconds} seconds")
