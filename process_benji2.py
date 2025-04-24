# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import numpy as np
import os
import csv
cwd = os.getcwd()
print(cwd)
class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: float = 1.0  # For unit conversions
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

wheelbase_in = 60.125
wd_front = .52
imu_offset_in = 13.25

inch_to_m = .0254
mg_to_ms2 = 9.80665/1000
mdps_to_rads = np.pi / 180 / 1000
ms2_to_g = 1/9.80665

wheelbase_m = wheelbase_in*inch_to_m
imu_offset_m = imu_offset_in*inch_to_m
cg_from_front_m = wd_front * wheelbase_m
r_imucg = np.array([cg_from_front_m - imu_offset_m,0,0])


def parseBenji2File(number: int, path: str, session: str):
    binary_name = path + "data25_" + str(number) + ".benji2"
    csv_name = "processed/" + session + "/data" + str(number) + ".csv"
    with open(binary_name, 'br') as f:
        with open(csv_name, 'w') as csv:

            # Get the Length of the Header String
            data = f.read(4)
            headerLen = int.from_bytes(data, "little", signed=False) - 2

            # print(headerLen)
            # Grab the Header String
            data = f.read(headerLen)
            header = data.decode("utf-8")
            filtered_header, dataSize = filter_duplicate_headers(header)

            deviceList = [key.strip() for key in filtered_header.split(",")]

            devices = []
            for i in range(len(deviceList)):
                devices.append(device_data(deviceList[i], i, dataSize[i]))

            print("Devices:", deviceList)
            print("Data sizes:", dataSize)

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
                        device.conversion_factor = lambda v: ((4.7 / 10) * (v - 1432))
                    case "FR_SG":
                        device.conversion_factor = lambda v: (-(4.7 / 9.24) * (v - 63608))
                    case "RL_SG":
                        device.conversion_factor = lambda v: ((4.7 / 7.3) * (v - 931))
                    case "FLW_AMB" | "FRW_AMB" | "RLW_AMB" | "RRW_AMB" | \
                         "FLW_RTR" | "FRW_RTR" | "RLW_RTR" | "RRW_RTR":
                        device.conversion_factor = lambda v: ((v*.02) - 273.15)
                    case "IMU_X_ACCEL" | "IMU_Y_ACCEL" | "IMU_Z_ACCEL" | \
                         "IMU_X_GYRO"  | "IMU_Y_GYRO" | "IMU_Z_GYRO":
                        device.signed = True
                    # case "IMU_X_ACCEL":
                    #     device.signed = True
                    # case "IMU_Y_ACCEL":
                    #     device.signed = True
                    # case "IMU_Z_ACCEL":
                    #     device.signed = True    
                    # case "IMU_X_GYRO":
                    #     device.signed = True
                    # case "IMU_Y_GYRO":
                    #     device.signed = True
                    # case "IMU_Z_GYRO":
                    #     device.signed = True
                    # case "FLW_AMB":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "FRW_AMB":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "RLW_AMB":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "RRW_AMB":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "FLW_RTR":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "FRW_RTR":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "RLW_RTR":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    # case "RRW_RTR":
                    #     device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
                    
                    case _:
                        pass  # Default case
                
                
            # dataList = np.zeros(device_cnt)
            # dataSize = []

            csv.write("," + filtered_header + ", IMU_X_CG_ACCEL_G, IMU_Y_CG_ACCEL_G, IMU_Z_CG_ACCEL_G\n")
     
            f.read(2)

            # data = f.read(devices[0].byte_size)
            # print(f"Init Time: {int.from_bytes(data, "big")/1000}")
            
            # Get the initialization time
            data = f.read(devices[0].byte_size)
            init = devices[0].getData(data)
            last = init
            omega_prev = np.zeros(3)
            count = 0

            # f.seek(-4, os.SEEK_CUR)
            f.seek(-devices[0].byte_size,os.SEEK_CUR)
            
            while True:
                # Parallel Array to the header
                outputList = [None] * len(devices)
                # for device in devices:
                #     if(device.name == "CH_COUNT"):
                #         break

                #     data = f.read(device.byte_size)
                #     if data == None:
                #         break

                #     outputList[device.column_index] = device.getData(data)
                for device in devices:
                    data = f.read(device.byte_size)
                    if not data:
                        return  # EOF
                    outputList[device.column_index] = device.getData(data)

                # Compute dt using timestamp at index 0
                curr = outputList[0]
                dt = (curr - last) if count > 0 else 0.0
                last = curr

                # Raw IMU in SI
                a_raw = np.array([
                    outputList[deviceList.index('IMU_X_ACCEL')],
                    outputList[deviceList.index('IMU_Y_ACCEL')],
                    outputList[deviceList.index('IMU_Z_ACCEL')]
                ]) * mg_to_ms2
                omega_raw = np.array([
                    outputList[deviceList.index('IMU_X_GYRO')],
                    outputList[deviceList.index('IMU_Y_GYRO')],
                    outputList[deviceList.index('IMU_Z_GYRO')]
                ]) * mdps_to_rads

                # Angular acceleration
                alpha = (omega_raw - omega_prev) / dt if dt > 0 else np.zeros(3)
                omega_prev = omega_raw

                # CG-corrected accel in G
                a_cg = a_raw + np.cross(alpha, r_imucg) + np.cross(omega_raw, np.cross(omega_raw, r_imucg))
                a_cg_g = a_cg * ms2_to_g

                #last=outputList[0]
                count += 1
                outputList.insert(0,count)
                outputList.extend(a_cg_g.tolist())

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



            
for i in range(149, 150): 
    parseBenji2File(str(i), "data/250423/", "250423")