# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import numpy as np
import os
import csv
from devices import create_devices, configure_devices
from imu_displacement import translate_linear_acc

# GUI helpers for folder dialogs
import tkinter as tk
from tkinter import filedialog


def filter_duplicate_headers(header_str):
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


def parseBenji2File(input_dir: str, output_dir: str, session: str):
    """
    Process all .benji2 files in input_dir and write matching CSVs to output_dir/session
    """
    in_path = Path(input_dir)
    out_base = Path(output_dir) / session
    out_base.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {out_base.resolve()}")

    benji_files = list(in_path.glob("*.benji2"))
    print(f"Found {len(benji_files)} .benji2 files in {in_path}")

    for benji_path in benji_files:
        print(f"Processing {benji_path.name}")
        csv_path = out_base / (benji_path.stem + ".csv")
        with open(benji_path, "br") as f, open(csv_path, "w", newline="") as csvfile:
            # Get the Length of the Header String
            data = f.read(4)
            headerLen = int.from_bytes(data, "little", signed=False) - 1

            # Handle log files that were not written to by logger 26
            if(headerLen <= 0):
                print("Empty Log File! Skipping %s", benji_path)
                continue

            # Grab the Header String
            data = f.read(headerLen)
            try:
                header = data.decode("utf-8")
            except UnicodeDecodeError as e:
                print(f"Error decoding header for {benji_path}: {e}. Skipping file.")
                continue
            filtered_header, dataSize = filter_duplicate_headers(header)

            deviceList = [key.strip() for key in filtered_header.split(",")]
            devices = create_devices(deviceList, dataSize)
            configure_devices(devices)

            # write header and prepare to read data rows
            csvfile.write("," + filtered_header + "\n")

            f.read(1)

            # # Get the initialization time
            # data = f.read(devices[0].byte_size)
            # init = devices[0].getData(data)
            # last = init
            count = 0
            # f.seek(-devices[0].byte_size, os.SEEK_CUR)

            while True:
                # Parallel Array to the header
                outputList = [None] * len(devices)
                eof = False
                for device in devices:
                    if device.name == "CH_COUNT":
                        break

                    data = f.read(device.byte_size)
                    if not data:
                        eof = True
                        break

                    outputList[device.column_index] = device.getData(data)

                if eof:
                    break

                count += 1
                outputList.insert(0, count)

                # Write the current row to the CSV file
                try:
                    csvfile.write(",".join(str(val) if val is not None else "" for val in outputList) + "\n")
                except Exception as e:
                    print(f"Error writing row: {e}")
                    print(f"Row data: {outputList}")
                    continue
            

        # Adds 3 channels to csv file: CG_X_ACCEL, CG_Y_ACCEL, CG_Z_ACCEL
        translate_linear_acc( csv_path )
    
    print("Processing complete.")


            

def main():
    # hide root window
    root = tk.Tk()
    root.withdraw()

    input_dir = filedialog.askdirectory(title="Select input directory with .benji2 files")
    if not input_dir:
        print("No input directory selected. Exiting.")
        root.destroy()
        return
    print(f"Selected input directory: {input_dir}")

    output_dir = filedialog.askdirectory(title="Select output base directory")
    if not output_dir:
        print("No output directory selected. Exiting.")
        root.destroy()
        return
    print(f"Selected output directory: {output_dir}")

    # derive session name from input directory basename
    session = f"processed_{Path(input_dir).name}"
    print(f"Using session name '{session}' derived from input folder")

    root.destroy()
    parseBenji2File(input_dir, output_dir, session)


if __name__ == "__main__":
    main()