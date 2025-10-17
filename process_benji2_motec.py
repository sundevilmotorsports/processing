#!/usr/bin/env python3

import os
from pathlib import Path
from datetime import datetime

# Import MoTeC format classes
try:
    from motec_ld import MotecLog, MotecChannel, MotecEvent
except ImportError as e:
    print(f"Error importing MoTeC format library: {e}")
    print("Make sure motec_ld.py is in the same folder")
    exit(1)


# Hard-coded channel mapping (from CSV → MoTeC)
ALL_CHANNELS = [
    # (benj2_index, display_name, short_name, units)
    (0, "Time", "Time", "s"),                # TS
    (1, "Front Brake Pressure", "F_BrkPrs", "kPa"),  # F_BRAKEPRESSURE
    (2, "Rear Brake Pressure", "R_BrkPrs", "kPa"),   # R_BRAKEPRESSURE
    (3, "Steering", "Steering", "deg"),     # STEERING
    (4, "FL Shock", "FL_Shock", "mm"),      # FLSHOCK
    (5, "FR Shock", "FR_Shock", "mm"),      # FRSHOCK
    (6, "RR Shock", "RR_Shock", "mm"),      # RRSHOCK
    (7, "RL Shock", "RL_Shock", "mm"),      # RLSHOCK
    (8, "Current", "Current", "A"),         # CURRENT
    (9, "Battery Voltage", "Battery", "V"), # BATTERY
    (10, "IMU X Accel", "IMU_X", "g"),
    (11, "IMU Y Accel", "IMU_Y", "g"),
    (12, "IMU Z Accel", "IMU_Z", "g"),
    (13, "IMU X Gyro", "Gyro_X", "deg/s"),
    (14, "IMU Y Gyro", "Gyro_Y", "deg/s"),
    (15, "IMU Z Gyro", "Gyro_Z", "deg/s"),
    (16, "FR Strain Gauge", "FR_SG", "raw"),
    (17, "FL Strain Gauge", "FL_SG", "raw"),
    (18, "RL Strain Gauge", "RL_SG", "raw"),
    (19, "RR Strain Gauge", "RR_SG", "raw"),
    # Add more channels as needed, matching your logger order
]


class device_data:
    def __init__(self, name, column_index, byte_size, conversion_factor=1.0, signed=False, byte_order="big"):
        self.name = name
        self.column_index = column_index
        self.byte_size = byte_size
        self.conversion_factor = conversion_factor
        self.signed = signed
        self.byte_order = byte_order

    def getData(self, data: bytes):
        value = int.from_bytes(data, byteorder=self.byte_order, signed=self.signed)
        if callable(self.conversion_factor):
            return self.conversion_factor(value)
        return value * self.conversion_factor


def filter_duplicate_headers(header_str):
    headers = [h.strip() for h in header_str.split(',')]
    base_counts = {}
    filtered = []
    for header in headers:
        base = header.rstrip('0123456789').strip()
        if base not in base_counts:
            filtered.append(base)
            base_counts[base] = 1
        else:
            base_counts[base] += 1
    return filtered, base_counts


def parse_benj2_to_samples(file_path):
    with open(file_path, 'br') as f:
        # Read header length
        data = f.read(4)
        header_len = int.from_bytes(data, "little") - 2
        header_bytes = f.read(header_len)
        header_str = header_bytes.decode("utf-8")
        filtered_header, counts = filter_duplicate_headers(header_str)

        # trying to see stuff
        print(f"[DEBUG] Header length: {header_len}")
        print(f"[DEBUG] Raw header string: {header_str}")
        print(f"[DEBUG] Filtered headers: {filtered_header}")   

        # Create devices
        devices = [device_data(name, i, 2) for i, name in enumerate(filtered_header)]  # default byte_size=2
        print(f"[DEBUG] Created {len(devices)} device_data entries")
        for d in devices:
            print(f"   - {d.name} (col {d.column_index}, size {d.byte_size}, factor {d.conversion_factor}, signed={d.signed})")


        # Apply conversions
        for d in devices:
            match d.name:
                case "TS": d.conversion_factor = 1/1000
                case "CURRENT": d.conversion_factor = 1.25; d.signed = True
                case "BATTERY": d.conversion_factor = 1.25/1000; d.signed = True
                case "FL_SG": d.conversion_factor = lambda v: (-11052026.1 * v + 2606.22253)
                case "FR_SG": d.conversion_factor = lambda v: v
                case "RL_SG": d.conversion_factor = lambda v: (-1401922.44 * v + 92026.0137)
                case "RR_SG": d.conversion_factor = lambda v: v
                case _:
                    pass

        # Skip 2 bytes
        f.read(2)
        # Init time
        init_time_bytes = f.read(devices[0].byte_size)
        init_time = devices[0].getData(init_time_bytes)
        f.seek(-4, os.SEEK_CUR)

        # Read all samples
        samples = []
        while True:
            row = []
            for device in devices:
                d_bytes = f.read(device.byte_size)
                if not d_bytes:

                    # printing studf
                    print(f"[DEBUG] Total samples parsed: {len(samples)}")
                    print(f"[DEBUG] First 3 parsed rows:")
                    for row in samples[:3]:
                        print(row)

                    return samples
                row.append(device.getData(d_bytes))
            samples.append(row)


def convert_benj2_to_motec(file_path):
    print(f"Processing {file_path}...")
    samples = parse_benj2_to_samples(file_path)

    if not samples:
        print("No samples found!")
        return

    # Create MoTeC log
    log = MotecLog()
    now = datetime.now()
    log.date = now.strftime('%d/%m/%Y')
    log.time = now.strftime('%H:%M:%S')
    log.driver = "Driver"
    log.vehicle = "Vehicle"
    log.venue = "Track"
    log.comment = "Benj2 → MoTeC"

    log.event = MotecEvent({
        "name": "Full Data Session",
        "session": "All Channels",
        "comment": f"{len(ALL_CHANNELS)} channels",
        "venuepos": 0
    })

    # Add channels
    freq = 500  # default
    for i, (col_idx, display_name, short_name, units) in enumerate(ALL_CHANNELS):
        channel_def = {
            "name": display_name,
            "shortname": short_name[:8],
            "units": units,
            "id": 8000 + i,
            "freq": freq,
            "shift": 0,
            "multiplier": 1,
            "scale": 1,
            "decplaces": 2,
            "datatype": 0x07,
            "datasize": 4
        }
        log.add_channel(MotecChannel(channel_def))

    # Add samples, using logger's TS column (already scaled in parse_benj2_to_samples)
    for row in samples:
        row_out = []
        for col_idx, _, _, _ in ALL_CHANNELS:
            row_out.append(row[col_idx])
        log.add_samples(row_out)


    # Write file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / (Path(file_path).stem + ".ld")
    with open(output_file, 'wb') as f:
        f.write(log.to_string())


    print(f"[DEBUG] Writing to: {output_file.resolve()}")

    print(f"✓ MoTeC file written: {output_file} ({len(samples)} samples, {len(ALL_CHANNELS)} channels)")

    # print first 10 TS values from logger
    print("\nFirst 10 TS values (seconds from logger):")
    for i in range(min(10, len(samples))):
        print(f"Sample {i}: {samples[i][0]:.3f} s")


    return output_file



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert a Benj2 file to MoTeC")
    parser.add_argument("input_file", help="Path to .benji2 file")
    args = parser.parse_args()

    convert_benj2_to_motec(args.input_file)
