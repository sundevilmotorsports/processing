#!/usr/bin/env python3

import os
from pathlib import Path
from multiprocessing import Pool, cpu_count
from time import time
import csv
from tqdm import tqdm

# --- device_data class as before ---
class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: float = 1.0
    signed: bool = False
    byte_order: str = "big"

    def __init__(self, name: str, column_index: int, byte_size: int, conversion_factor: float = 1.0, signed: bool = False, byte_order: str = "big"):
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

# --- header filtering ---
def filter_duplicate_headers(header_str: str):
    headers = [h.strip() for h in header_str.split(',')]
    base_counts = {}
    filtered = []

    for header in headers:
        header = header.strip('\x00')
        base = header.rstrip('0123456789').strip()
        if base not in base_counts:
            filtered.append(base)
            base_counts[base] = 1
        else:
            base_counts[base] += 1

    counts = [base_counts[base] for base in filtered]
    return ','.join(filtered), counts

# --- parsing single file and writing CSV ---
def parseBenji2File(file_path: str, output_dir: str):
    start_time = time()
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_name = output_dir / (file_path.stem + ".csv")

    with open(file_path, 'br') as f, open(csv_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # header
        data = f.read(4)
        headerLen = int.from_bytes(data, "little") - 2
        data = f.read(headerLen)
        header_str = data.decode("utf-8")
        filtered_header, dataSize = filter_duplicate_headers(header_str)
        deviceList = [key.strip() for key in filtered_header.split(",")]

        devices = [device_data(deviceList[i], i, dataSize[i]) for i in range(len(deviceList))]

        # conversions
        for device in devices:
            match device.name:
                case "TS": device.conversion_factor = 1/1000
                case "CURRENT": device.conversion_factor = 1.25; device.signed = True
                case "BATTERY": device.conversion_factor = 1.25 / 1000; device.signed = True
                case "FL_SG": device.conversion_factor = lambda v: (-11052026.1 * v + 2606.22253)
                case "FR_SG": device.conversion_factor = lambda v: (v)
                case "RL_SG": device.conversion_factor = lambda v: (-1401922.44 * v + 92026.0137)
                case "RR_SG": device.conversion_factor = lambda v: (v)
                case "IMU_X_ACCEL" | "IMU_Y_ACCEL" | "IMU_Z_ACCEL" | "IMU_X_GYRO" | "IMU_Y_GYRO" | "IMU_Z_GYRO":
                    device.signed = True
                case _:
                    pass

        writer.writerow(["Index"] + deviceList)

        # skip 2 bytes
        f.read(2)

        # init time
        f.read(devices[0].byte_size)  # discard init
        f.seek(-4, os.SEEK_CUR)

        count = 0
        while True:
            row = [None] * len(devices)
            for device in devices:
                d_bytes = f.read(device.byte_size)
                if not d_bytes:
                    break
                row[device.column_index] = device.getData(d_bytes)
            else:
                count += 1
                writer.writerow([count] + row)
                continue
            break  # EOF

    elapsed = time() - start_time
    return (file_path.name, count, elapsed, csv_name)

# --- top-level wrapper for multiprocessing ---
def process_file(args):
    file_path, output_dir = args
    name, rows, elapsed, csv_file = parseBenji2File(file_path, output_dir)
    print(f"[OK] {name}: {rows} rows in {elapsed:.2f}s → {csv_file}")
    return csv_file

# --- directory processing ---


def process_directory(input_dir: str, output_dir: str = "output"):
    input_dir = Path(input_dir)
    files = sorted(input_dir.glob("*.benji2"))
    if not files:
        print(f"[WARN] No .benji2 files found in {input_dir}")
        return

    print(f"[INFO] Found {len(files)} files. Using {cpu_count()} cores...")

    args = [(str(f), output_dir) for f in files]

    start_total = time()
    with Pool() as pool:
        results = list(tqdm(pool.imap_unordered(process_file, args), total=len(args), desc="Processing files"))
    total_elapsed = time() - start_total

    print(f"\n[INFO] All files processed. CSVs in {output_dir}")
    print(f"[INFO] Total files: {len(results)}")
    print(f"[INFO] Total runtime: {total_elapsed:.2f}s")

# def process_directory(input_dir: str, output_dir: str = "output"):
#     input_dir = Path(input_dir)
#     files = sorted(input_dir.glob("*.benji2"))
#     if not files:
#         print(f"[WARN] No .benji2 files found in {input_dir}")
#         return

#     print(f"[INFO] Found {len(files)} files. Using {cpu_count()} cores...")

#     args = [(str(f), output_dir) for f in files]

#     with Pool() as pool:
#         results = list(tqdm(pool.imap_unordered(process_file, args), total=len(args), desc="Processing files"))

#     print(f"[INFO] All files processed. CSVs in {output_dir}")

# --- main ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert Benji2 files to CSV (parallel, with progress)")
    parser.add_argument("input_path", help="Path to .benji2 file or directory")
    parser.add_argument("--output", default="output", help="Directory to save CSVs")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if input_path.is_file() and input_path.suffix.lower() == ".benji2":
        parseBenji2File(str(input_path), args.output)
    elif input_path.is_dir():
        process_directory(str(input_path), args.output)
    else:
        print(f"[ERROR] {input_path} is not a valid file or directory")
