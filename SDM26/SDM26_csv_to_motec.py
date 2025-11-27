#!/usr/bin/env python3

import csv
import sys
import os
from datetime import datetime

# Import MoTeC format classes from local file
try:
    from motec_ld import MotecLog, MotecChannel, MotecEvent
except ImportError as e:
    print(f"Error importing MoTeC format library: {e}")
    print(f"Make sure motec_ld.py is in the same folder")
    sys.exit(1)

# ALL channels from CSV (header names only)
ALL_CHANNELS = [
    # (csv_header_name, display_name, short_name, units)
    ("TS", "Time", "Time", "s"),
    ("F_BRAKEPRESSURE", "Front Brake Pressure", "F_BrkPrs", "kPa"),
    ("R_BRAKEPRESSURE", "Rear Brake Pressure", "R_BrkPrs", "kPa"),
    ("STEERING", "Steering", "Steering", "deg"),
    ("FLSHOCK", "FL Shock", "FL_Shock", "mm"),
    ("FRSHOCK", "FR Shock", "FR_Shock", "mm"),
    ("RRSHOCK", "RR Shock", "RR_Shock", "mm"),
    ("RLSHOCK", "RL Shock", "RL_Shock", "mm"),
    ("CURRENT", "Current", "Current", "A"),
    ("BATTERY", "Battery Voltage", "Battery", "V"),
    ("IMU_X_ACCEL", "IMU X Accel", "IMU_X", "G"),
    ("IMU_Y_ACCEL", "IMU Y Accel", "IMU_Y", "G"),
    ("IMU_Z_ACCEL", "IMU Z Accel", "IMU_Z", "G"),
    ("IMU_X_GYRO", "IMU X Gyro", "Gyro_X", "deg/s"),
    ("IMU_Y_GYRO", "IMU Y Gyro", "Gyro_Y", "deg/s"),
    ("IMU_Z_GYRO", "IMU Z Gyro", "Gyro_Z", "deg/s"),
    ("FR_SG", "FR Strain Gauge", "FR_SG", "raw"),
    ("FL_SG", "FL Strain Gauge", "FL_SG", "raw"),
    ("RL_SG", "RL Strain Gauge", "RL_SG", "raw"),
    ("RR_SG", "RR Strain Gauge", "RR_SG", "raw"),
    ("FLW_AMB", "FL Wheel Ambient", "FLW_Amb", "C"),
    ("FLW_OBJ", "FL Wheel Object", "FLW_Obj", "raw"),
    ("FLW_RPM", "FL Wheel RPM", "FLW_RPM", "rpm"),
    ("FRW_AMB", "FR Wheel Ambient", "FRW_Amb", "C"),
    ("FRW_OBJ", "FR Wheel Object", "FRW_Obj", "raw"),
    ("FRW_RPM", "FR Wheel RPM", "FRW_RPM", "rpm"),
    ("RRW_AMB", "RR Wheel Ambient", "RRW_Amb", "C"),
    ("RRW_OBJ", "RR Wheel Object", "RRW_Obj", "raw"),
    ("RRW_RPM", "RR Wheel RPM", "RRW_RPM", "rpm"),
    ("RLW_AMB", "RL Wheel Ambient", "RLW_Amb", "C"),
    ("RLW_OBJ", "RL Wheel Object", "RLW_Obj", "raw"),
    ("RLW_RPM", "RL Wheel RPM", "RLW_RPM", "rpm"),
    ("BRAKE_FLUID", "Brake Fluid", "BrkFluid", "raw"),
    ("THROTTLE_LOAD", "Throttle Load", "Throttle", "%"),
    ("BRAKE_LOAD", "Brake Load", "Brake", "%"),
    ("DRS", "DRS", "DRS", "bool"),
    ("GPS_LON", "GPS Longitude", "GPS_Lon", "deg"),
    ("GPS_LAT", "GPS Latitude", "GPS_Lat", "deg"),
    ("GPS_SPD", "GPS Speed", "GPS_Spd", "kph"),
    ("GPS_FIX", "GPS Fix", "GPS_Fix", "bool"),
    ("ECT", "Engine Coolant Temp", "ECT", "C"),
    ("OIL_PSR", "Oil Pressure", "Oil_Prs", "kPa"),
    ("TPS", "TPS", "TPS", "%"),
    ("APS", "APS", "APS", "%"),
    ("DRIVEN_WSPD", "Driven Wheel Speed", "DrWSpeed", "kph"),
    ("TESTNO", "Test Number", "TestNo", "num"),
    ("DTC_FLW", "DTC FL Wheel", "DTC_FLW", "code"),
    ("DTC_FRW", "DTC FR Wheel", "DTC_FRW", "code"),
    ("DTC_RLW", "DTC RL Wheel", "DTC_RLW", "code"),
    ("DTC_RRW", "DTC RR Wheel", "DTC_RRW", "code"),
    ("DTC_FLSG", "DTC FL Strain", "DTC_FLSG", "code"),
    ("DTC_FRSG", "DTC FR Strain", "DTC_FRSG", "code"),
    ("DTC_RLSG", "DTC RL Strain", "DTC_RLSG", "code"),
    ("DTC_RRSG", "DTC RR Strain", "DTC_RRSG", "code"),
    ("DTC_IMU", "DTC IMU", "DTC_IMU", "code"),
    ("GPS_0_", "GPS 0", "GPS_0", "raw"),
    ("GPS_1_", "GPS 1", "GPS_1", "raw"),
    ("CH_COUNT", "Channel Count", "CH_Count", "num"),
    ("FR_Wheel_Speed", "FR Wheel Speed", "FR_wspd", "kph"),
    ("FL_Wheel_Speed", "FL Wheel Speed", "FL_wspd", "kph")

]


def read_csv_file(csv_path, max_samples=None):
    print(f"Reading {csv_path}...")
    data = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []
        for i, row in enumerate(reader):
            if max_samples and i >= max_samples:
                break
            data.append(row)
    print(f"Read {len(data)} samples from {os.path.basename(csv_path)}")
    return header, data


def convert_csv_to_motec_fixed(csv_path, output_filename, max_samples=None):
    """Convert ALL CSV columns to MoTeC with FIXED encoding"""
    
    print("Converting CSV to MoTeC")
    print("=" * 60)

    header, data = read_csv_file(csv_path, max_samples)

    # Build a case-insensitive header map for lookup
    header_map = {h.strip().lower(): idx for idx, h in enumerate(header)} if header else {}

    # Determine time column index (prefer header name "TS" from ALL_CHANNELS)
    time_col_name = ALL_CHANNELS[0][0]

    # Default frequency
    freq = 500

    time_idx = header_map.get(time_col_name.strip().lower())
    if time_idx is None:
        print(f"Warning: time column '{time_col_name}' not found in CSV header; using default sample rate {freq} Hz")
    else:
        # Calculate frequency from first two samples if possible
        if len(data) >= 2:
            try:
                dt = float(data[1][time_idx]) - float(data[0][time_idx])
                if dt > 0:
                    freq = int(1.0 / dt)
            except Exception:
                pass
    print(f"Sample rate: {freq} Hz")
    
    # Create MoTeC log
    log = MotecLog()
    now = datetime.now()
    log.date = now.strftime('%d/%m/%Y')
    log.time = now.strftime('%H:%M:%S')
    log.driver = "Driver"
    log.vehicle = "Vehicle"
    log.venue = "Track"
    log.comment = "Fixed - All Channels"
    
    # Create event
    log.event = MotecEvent({
        "name": "Full Data Session",
        "session": "All Channels Fixed",
        "comment": f"All {len(ALL_CHANNELS)} channels with decplaces=0",
        "venuepos": 0
    })
    
    # Add ALL channels
    print(f"\nAdding {len(ALL_CHANNELS)} channels...")
    channels_added = []
    
    for i, (csv_name, display_name, short_name, units) in enumerate(ALL_CHANNELS):
        try:
            channel_def = {
                "name": display_name,
                "shortname": short_name[:8],
                "units": units,
                "id": 8000 + i,
                "freq": freq,
                "shift": 0,
                "multiplier": 1,
                "scale": 1,
                "decplaces": 0,
                "datatype": 0x07,
                "datasize": 4
            }
            channel = MotecChannel(channel_def)
            log.add_channel(channel)
            # Resolve the CSV column index by header name (case-insensitive).
            resolved_index = header_map.get(csv_name.strip().lower()) if header else None
            if resolved_index is None:
                print(f"Warning: dropping channel '{display_name}' (CSV header '{csv_name}') — header not found")
                # remove the channel we just added from the log
                # MotecLog keeps channels in a list; pop the last added channel
                try:
                    log.channels.pop()
                    log.numchannels = len(log.channels)
                except Exception:
                    pass
                continue
            channels_added.append((resolved_index, csv_name))
            if i < 10 or i % 10 == 0:
                print(f"  [{i+1:2}/{len(ALL_CHANNELS)}] {display_name:25} (header '{csv_name}', {units})")
        except Exception as e:
            print(f"  ERROR adding {display_name}: {e}")
    
    print(f"\nSuccessfully added {len(channels_added)} channels")
    
    # Add samples
    print(f"\nConverting samples...")
    sample_count = 0
    for row_idx, row in enumerate(data):
        samples = []
        for col_idx, csv_name in channels_added:
            try:
                val_str = row[col_idx]
                if val_str == 'None' or val_str == '':
                    val = 0.0
                else:
                    val = float(val_str)
                samples.append(val)
            except (IndexError, ValueError):
                samples.append(0.0)
        log.add_samples(samples)
        sample_count += 1
    
    print(f"\nConversion complete:")
    print(f"  Samples converted: {sample_count}")
    
    # Write output to csv-to-motec/output folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"\nWriting to {output_path}...")
    with open(output_path, 'wb') as f:
        f.write(log.to_string())
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"\n✓ SUCCESS!")
    print(f"  File: {output_filename}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Channels: {len(channels_added)}")
    print(f"  Samples: {sample_count}")
    
    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert CSV(s) to MoTeC format')
    parser.add_argument('input_path', help='Path to CSV file OR folder of CSVs to convert')
    parser.add_argument('--samples', '-s', type=int, default=None,
                       help='Max samples to convert (default: all)')
    args = parser.parse_args()
    
    if not os.path.exists(args.input_path):
        print(f"Error: Path not found: {args.input_path}")
        sys.exit(1)

    # Case 1: Single CSV
    if os.path.isfile(args.input_path) and args.input_path.endswith(".csv"):
        csv_files = [args.input_path]
    # Case 2: Folder of CSVs
    elif os.path.isdir(args.input_path):
        csv_files = [
            os.path.join(args.input_path, f) 
            for f in os.listdir(args.input_path) if f.endswith(".csv")
        ]
        if not csv_files:
            print("No CSV files found in folder.")
            sys.exit(1)
    else:
        print("Error: Input must be a CSV file or a folder containing CSVs.")
        sys.exit(1)

    # Process all CSVs
    for csv_file in csv_files:
        csv_basename = os.path.splitext(os.path.basename(csv_file))[0]
        output_filename = f"{csv_basename}.ld"
        output_path = convert_csv_to_motec_fixed(csv_file, output_filename, args.samples)
        print("\n" + "=" * 60)
        print("DONE! Load in MoTeC i2:")
        print(f"  File location: {output_path}")


if __name__ == '__main__':
    main()
