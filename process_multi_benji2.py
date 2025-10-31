# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import concurrent.futures
import multiprocessing
import numpy as np
import os
import csv
import time
# cwd = os.getcwd()
# print(cwd)
class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: float = 1.0  # unit conversions
    signed: bool = False
    byte_order: str = "big"

    def __init__(self, name: str, column_index: int, byte_size: int, conversion_factor: float = 1.0, signed: bool = False, byte_order: str = "big"):
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



def parseBenji2File(number: int, path: str, session: str):
    binary_name = path + "data24_" + str(number) + ".benji2"
    csv_name = "output/" + session + "/data24_" + str(number) + ".csv"
    # make sure output directory exists
    Path(csv_name).parent.mkdir(parents=True, exist_ok=True)

    with open(binary_name, 'br') as f:
        with open(csv_name, 'w', newline='') as csvfile:

            # Get the Length of the Header String
            data = f.read(4)
            headerLen = int.from_bytes(data, "little", signed=False) - 2

            print(headerLen)


            # Grab the Header String
            data = f.read(headerLen)
            header = data.decode("utf-8")
            filtered_header, dataSize = filter_duplicate_headers(header)

            deviceList = [key.strip() for key in filtered_header.split(",")]

            devices = []
            for i in range(len(deviceList)):
                devices.append(device_data(deviceList[i], i, dataSize[i]))

            # TODO: Do any column swaps here by changing device.column_index, make sure to swap both devices
            for device in devices:
                match device.name:
                    case "TS":
                        device.conversion_factor = 1/1000
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
                    case "IMU_Y_GYRO":
                        device.signed = True
                    case "IMU_Z_GYRO":
                        device.signed = True
                    case "FLW_AMB":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "FRW_AMB":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "RLW_AMB":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "RRW_AMB":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "FLW_RTR":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "FRW_RTR":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "RLW_RTR":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    case "RRW_RTR":
                        device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    
                    case _:
                        pass  # Default case
                
                
            # dataList = np.zeros(device_cnt)
            # dataSize = []


            # Write CSV header; first column will be the row counter
            csvfile.write("," + filtered_header + "\n")
            


            f.read(2)

            # data = f.read(devices[0].byte_size)
            # print(f"Init Time: {int.from_bytes(data, "big")/1000}")

            
            # Get the initialization time
            data = f.read(devices[0].byte_size)
            init = devices[0].getData(data)
            last = init
            count = 0
            f.seek(-4, os.SEEK_CUR)
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
                csvfile.write(','.join(str(val) for val in outputList) + "\n")




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



            
def _extract_number_from_filename(path: Path) -> str:
    name = path.stem  # data24_200
    if name.startswith('data24_'):
        return name.split('_', 1)[1]
    return name


def process_directory(input_dir: str, session: str, max_workers: int | None = None):
    """Process all data24_*.benji2 files in input_dir in parallel."""
    start_time = time.time()
    
    p = Path(input_dir)
    files = sorted(p.glob('data24_*.benji2'))
    if not files:
        print(f"No .benji2 files found in {input_dir}")
        return

    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)

    print(f"Processing {len(files)} files with {max_workers} workers...")

    # Prepare jobs: extract numeric suffix for each file
    jobs = [( _extract_number_from_filename(fp), str(input_dir) if str(input_dir).endswith(os.sep) else str(input_dir)+os.sep, session) for fp in files]

    # Use ProcessPoolExecutor
    completed = 0
    total_files = len(files)
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = [exe.submit(parseBenji2File, num, path, sess) for (num, path, sess) in jobs]
        for fut in concurrent.futures.as_completed(futures):
            try:
                fut.result()
                completed += 1
                print(f"Progress: {completed}/{total_files} files processed ({(completed/total_files)*100:.1f}%)")
            except Exception as e:
                print(f"Error processing file: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds")
    print(f"Average time per file: {total_time/total_files:.2f} seconds")


if __name__ == '__main__':
    # Default input directory and session — change as needed or call process_directory from another script
    default_input = 'data_benji/'
    default_session = 'csv'
    process_directory(default_input, default_session)