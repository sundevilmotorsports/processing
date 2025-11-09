# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import numpy as np
import os
import csv
# cwd = os.getcwd()
# print(cwd)
class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: float = 1.0  # For unit conversions
    signed: bool = False
    byte_order: str = "little"

    def __init__(self, name: str, column_index: int, byte_size: int, conversion_factor: float = 1.0, signed: bool = False, byte_order: str = "little"):
        self.name = name
        self.column_index = column_index
        self.byte_size = byte_size
        self.conversion_factor = conversion_factor
        self.signed = signed
        self.byte_order = byte_order
        return
    
    def getData(self, data: bytes):    
        value = int.from_bytes(data, byteorder=self.byte_order, signed=self.signed)
        if callable(self.conversion_factor):
            return self.conversion_factor(value)
        return value * self.conversion_factor



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

            # Grab the Header String
            data = f.read(headerLen)
            header = data.decode("utf-8")
            filtered_header, dataSize = filter_duplicate_headers(header)

            deviceList = [key.strip() for key in filtered_header.split(",")]

            devices = []
            for i in range(len(deviceList)):
                devices.append(device_data(deviceList[i], i, dataSize[i]))

            # Apply conversions / flags
            for device in devices:
                match device.name:
                    case "TS":
                        device.conversion_factor = 1e-6
                    case "CURRENT":
                        device.conversion_factor = 1.25
                        device.signed = True
                    case "BATTERY":
                        device.conversion_factor = 1.25 / 1000
                        device.signed = True
                    case "FL_SG":
                        device.conversion_factor = lambda v: (-11052026.1 * v + 2606.22253)
                    case "FR_SG":
                        device.conversion_factor = lambda v: (v)
                    case "RL_SG":
                        device.conversion_factor = lambda v: (-1401922.44 * v + 92026.0137)
                    case "RR_SG":
                        device.conversion_factor = lambda v: (v)
                    case "IMU_X_ACCEL":
                        device.signed = True
                    case "IMU_Y_ACCEL":
                        device.signed = True
                    case "IMU_Z_ACCEL":
                        device.signed = True    
                    case "IMU_X_GYRO":
                        device.signed = True
                        device.conversion_factor = lambda v: (v/65.6)
                    case "IMU_Y_GYRO":
                        device.signed = True
                        device.conversion_factor = lambda v: (v/65.6)
                    case "IMU_Z_GYRO":
                        device.signed = True
                        device.conversion_factor = lambda v: (v/65.6)
                    case "FLW_AMB" | "FRW_AMB" | "RLW_AMB" | "RRW_AMB" | "FLW_RTR" | "FRW_RTR" | "RLW_RTR" | "RRW_RTR":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "STEERING":
                        device.conversion_factor = lambda v: (((v / 1000) / 5) * 345)
                    case _:
                        pass

            # write header and prepare to read data rows
            csvfile.write("," + filtered_header + "\n")

            f.read(1)

            # Get the initialization time
            data = f.read(devices[0].byte_size)
            init = devices[0].getData(data)
            last = init
            count = 0
            f.seek(-devices[0].byte_size, os.SEEK_CUR)

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

                last = outputList[0]
                count += 1
                outputList.insert(0, count)

                # Write the current row to the CSV file
                csvfile.write(",".join(str(val) for val in outputList) + "\n")
            


            f.read(1)

            # data = f.read(devices[0].byte_size)
            # print(f"Init Time: {int.from_bytes(data, "big")/1000}")

            
            # Get the initialization time
            data = f.read(devices[0].byte_size)
            init = devices[0].getData(data)
            last = init
            count = 0
            f.seek(-devices[0].byte_size, os.SEEK_CUR)
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



            
parseBenji2File("data/26_can_testing", "processed", "can_test")