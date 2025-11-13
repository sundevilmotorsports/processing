# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import numpy as np
import os
import csv
from devices import create_devices, configure_devices


def parseBenji2File(input_dir: str, output_dir: str, session: str):
    """
    Process all .benji2 files in input_dir and write matching CSVs to output_dir/session
    """
    in_path = Path(input_dir)
    out_base = Path(output_dir) / session
    out_base.mkdir(parents=True, exist_ok=True)

    for benji_path in in_path.glob("*.benji2"):
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
            header = data.decode("utf-8")
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
                csvfile.write(",".join(str(val) for val in outputList) + "\n")
            


            f.read(1)

            # data = f.read(devices[0].byte_size)
            # print(f"Init Time: {int.from_bytes(data, "big")/1000}")

            
            # # Get the initialization time
            # data = f.read(devices[0].byte_size)
            # init = devices[0].getData(data)
            # last = init
            count = 0
            # f.seek(-devices[0].byte_size, os.SEEK_CUR)
            while data:
                # Parallel Array to the header
                outputList = [None] * len(devices)
                for device in devices:
                    if(device.name == "CH_COUNT"):
                        break

                    data = f.read(device.byte_size)
                    if data == None:
                        break

                    outputList[device.column_index] = device.getData(data)
                last=outputList[0]
                count += 1
                outputList.insert(0,count)

                # Write the current row to the CSV file
                csv.write(','.join(str(val) for val in outputList) + "\n")




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



            
parseBenji2File("data/skidpad_test_11_9", "processed", "new_skidpad_test_11_9")