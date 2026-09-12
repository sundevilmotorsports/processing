import cantools
import pandas as pd
import can
import os

file_absolute_path = os.path.abspath(__file__)

current_dir = os.path.dirname(file_absolute_path)

parent_dir = os.path.dirname(current_dir)

file_path = os.path.join(parent_dir, "SDM26.dbc")

# Import your existing, untouched processing file
from SDM26_benji2_to_csv import process, translate_linear_acc

def run_pipeline_from_sdm26(can_log_path, dbc_path, output_csv):
    # 1. Load YOUR exact database
    db = cantools.database.load_file(dbc_path)
    decoded_rows = []

    # 2. Decode the raw CAN data
    with can.LogReader(can_log_path) as reader:
        for msg in reader:
            try:
                msg_def = db.get_message_by_frame_id(msg.arbitration_id)
                signals = msg_def.decode(msg.data)
                
                # Add timestamp
                signals['TS'] = msg.timestamp
                decoded_rows.append(signals)
            except (KeyError, ValueError):
                continue

    # 3. Synchronize asynchronous CAN data into Benji2 format
    df = pd.DataFrame(decoded_rows)
    df = df.sort_values('TS').ffill().dropna()

    # 4. Map SDM26 DBC names to the names your script expects
    rename_map = {
        'IMU_ACCEL_X': 'IMU_X_ACCEL',
        'IMU_ACCEL_Y': 'IMU_Y_ACCEL',
        'IMU_ACCEL_Z': 'IMU_Z_ACCEL',
        'IMU_GYRO_X': 'IMU_X_GYRO',
        'IMU_GYRO_Y': 'IMU_Y_GYRO',
        'IMU_GYRO_Z': 'IMU_Z_GYRO',
        'FLSG_Strain': 'FL_SG',
        'FRSG_Strain': 'FR_SG',
        'RLSG_Strain': 'RL_SG',
        'RRSG_Strain': 'RR_SG',
        'FLWB_AmbTemp': 'FLW_AMB',
        'FLWB_ObjTemp': 'FLW_OBJ',
        'FLWB_rpm': 'FLW_RPM',
        'FRWB_AmbTemp': 'FRW_AMB',
        'FRWB_ObjTemp': 'FRW_OBJ',
        'FRWB_rpm': 'FRW_RPM',
        'ENGINE_aps': 'APS',
        'ENGINE_tps': 'TPS',
        'ENGINE_Driven_wspd': 'DRIVEN_WSPD',
        'ENGINE_OilPressure': 'OIL_PSR',
        'ENGINE_ect': 'ECT'
    }
    df = df.rename(columns=rename_map)

    # 5. Insert the CH_COUNT index column
    df.insert(0, 'CH_COUNT', range(len(df))) 

    # 6. Save and Run
    df.to_csv(output_csv, index=False)
    print(f"Intermediate CSV saved: {output_csv}")

    # Run your UNCHANGED processing file functions
    translate_linear_acc(output_csv)
    process(output_csv)
    print("Pipeline Complete.")

# Execution
run_pipeline_from_sdm26('your_car_log.blf', file_path, 'final_output.csv')