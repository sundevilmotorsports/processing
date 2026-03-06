# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import numpy as np
import os
import csv
import pandas as pd
from devices import create_devices, configure_devices
from imu_displacement import translate_linear_acc


def parseBenji2File(input_dir: str, output_dir: str, session: str):
    """
    Process all .benji2 files in input_dir and write matching CSVs to output_dir/session
    """
    in_path = Path(input_dir)
    out_base = Path(output_dir) / session
    out_base.mkdir(parents=True, exist_ok=True)

    for benji_path in in_path.glob("*.benji2"):
        csv_path = out_base / (benji_path.stem + ".csv")
        with open(benji_path, "br") as f: 
            # Get the Length of the Header String
            data = f.read(4)
            headerLen = int.from_bytes(data, "little", signed=False) - 1

            # Handle log files that were not written to by logger 26
            if(headerLen <= 0):
                print("Empty Log File! Skipping %s", benji_path)
                continue

            with open(csv_path, "w", newline="") as csvfile:

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
                """
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
                """

        # Adds 3 channels to csv file: CG_X_ACCEL, CG_Y_ACCEL, CG_Z_ACCEL
        translate_linear_acc( csv_path )
        process(csv_path)

        



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

def process(csv_path):
    df = pd.read_csv(csv_path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    if df.empty:
        print(f"WARNING: No data rows found in {csv_path}. Skipping processing.")
        return

    global_outliers = pd.Series(False, index=df.index)

    bounds_outliers = pd.Series(False, index=df.index)
    if "CG_X_ACCEL" in df.columns: bounds_outliers |= (df["CG_X_ACCEL"].abs() > 4.0) 
    if "CG_Y_ACCEL" in df.columns: bounds_outliers |= (df["CG_Y_ACCEL"].abs() > 4.0) 
    if "CG_Z_ACCEL" in df.columns: bounds_outliers |= (df["CG_Z_ACCEL"].abs() > 5.0) 
    if "F_BRAKEPRESSURE" in df.columns: bounds_outliers |= (df["F_BRAKEPRESSURE"] < 0)
    if "R_BRAKEPRESSURE" in df.columns: bounds_outliers |= (df["R_BRAKEPRESSURE"] < 0)
    global_outliers |= bounds_outliers

    sensors_to_check = [
        "CG_X_ACCEL", "CG_Y_ACCEL", "CG_Z_ACCEL", 
        "STEERING", 
        "FLSHOCK", "FRSHOCK", "RLSHOCK", "RRSHOCK"
    ]

    t = df["TS"].to_numpy()

    # --- Kalman Filter (improved) ---

    for col in sensors_to_check:
        if col not in df.columns:
            continue
            
        z_data = df[col].to_numpy()
        
        # If the sensor is completely dead/flatlined, skip the Kalman filter for it
        if len(np.unique(z_data)) <= 1:
            continue

        x = z_data[0]
        P = 1.0

        Q_base = 0.05
        R = 0.2
        threshold = 3.5

        kf_outliers = []

        identical_frames = 0
        last_z = z_data[0]

        for i in range(len(z_data)):
            z = z_data[i]

            if z == last_z:
                identical_frames += 1
            else:
                if identical_frames > 100:
                    x = z 
                    P = 1.0
                identical_frames = 0
                
            last_z = z

            # Time step
            dt = t[i] - t[i-1] if i > 0 else 0.01
            dt = 0.01 if (dt <= 0 or dt > 0.1) else dt

            # Predict
            Q = Q_base * dt
            x_pred = x
            P_pred = P + Q

            # Residual
            residual = z - x_pred
            S = P_pred + R

            # Mahalanobis distance
            mahal = abs(residual) / np.sqrt(S) if S > 0 else 0
            is_kf_outlier = mahal > threshold
            kf_outliers.append(is_kf_outlier)

            # Update
            K = (P_pred / S) if not is_kf_outlier else (0.01 * P_pred / S)
            x = x_pred + K * residual
            P = (1 - K) * P_pred

        global_outliers |= pd.Series(kf_outliers, index=df.index)

    df["OUTLIER"] = global_outliers


    df.to_csv(csv_path, index=False)
            
parseBenji2File("benji_files", "processed", "test_02_21")