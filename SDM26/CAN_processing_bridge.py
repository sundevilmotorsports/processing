import can
import cantools
import pandas as pd
from pathlib import Path

# Import your existing processing functions! 
# (Make sure this script is saved where it can import these, or adjust the import path)
from imu_displacement import translate_linear_acc
from  SDM26_benji2_to_csv import process # Replace 'your_main_script' with the actual file name

def process_can_log(log_filename, dbc_filename, output_csv_name):
    # 1. Bulletproof File Paths
    script_dir = Path(__file__).resolve().parent
    log_path = script_dir / log_filename
    dbc_path = script_dir / dbc_filename
    output_path = script_dir / output_csv_name

    if not log_path.exists():
        print(f"❌ ERROR: Cannot find CAN log at {log_path}")
        return
    if not dbc_path.exists():
        print(f"❌ ERROR: Cannot find DBC file at {dbc_path}")
        return

    print(f"Loading DBC: {dbc_path.name}...")
    db = cantools.database.load_file(str(dbc_path))
    
    decoded_rows = []
    print(f"Decoding CAN log: {log_path.name}...")

    # 2. Read and Decode the Raw CAN Data
    with can.LogReader(str(log_path)) as reader:
        for msg in reader:
            try:
                # Find the message definition in the DBC
                msg_def = db.get_message_by_frame_id(msg.arbitration_id)
                
                # Decode the binary data into real numbers using our exact math
                signals = msg_def.decode(msg.data)
                
                # Add the timestamp
                signals['TS'] = msg.timestamp
                decoded_rows.append(signals)
            except (KeyError, ValueError, cantools.database.errors.DecodeError):
                # Skip messages that aren't defined in our DBC
                continue

    if not decoded_rows:
        print("❌ ERROR: No data was decoded. Check if the log file matches the DBC.")
        return

    # 3. Format into a Pandas DataFrame
    print("Synchronizing data and formatting CSV...")
    df = pd.DataFrame(decoded_rows)
    
    # Sort by time and forward-fill missing data (since CAN sensors broadcast at different rates)
    df = df.sort_values('TS').ffill()

    # 4. Rename DBC signals to match what your `process()` script expects
    rename_map = {
        'IMU_ACCEL_X': 'IMU_X_ACCEL',
        'IMU_ACCEL_Y': 'IMU_Y_ACCEL',
        'IMU_ACCEL_Z': 'IMU_Z_ACCEL',
        'IMU_GYRO_X': 'IMU_X_GYRO',
        'IMU_GYRO_Y': 'IMU_Y_GYRO',
        'IMU_GYRO_Z': 'IMU_Z_GYRO',
        'FLWB_AmbTemp': 'FLW_AMB',
        'FLWB_ObjTemp': 'FLW_OBJ',
        'FLWB_rpm': 'FLW_RPM',
        'FRWB_AmbTemp': 'FRW_AMB',
        'FRWB_ObjTemp': 'FRW_OBJ',
        'FRWB_rpm': 'FRW_RPM',
        'RLWB_AmbTemp': 'RLW_AMB',
        'RLWB_ObjTemp': 'RLW_OBJ',
        'RLWB_rpm': 'RLW_RPM',
        'RRWB_AmbTemp': 'RRW_AMB',
        'RRWB_ObjTemp': 'RRW_OBJ',
        'RRWB_rpm': 'RRW_RPM',
        'FLSG_Strain': 'FL_SG',
        'FRSG_Strain': 'FR_SG',
        'RLSG_Strain': 'RL_SG',
        'RRSG_Strain': 'RR_SG'
        # STEERING, FLSHOCK, FRSHOCK, etc. are already named correctly!
    }
    df = df.rename(columns=rename_map)

    # 5. Insert the CH_COUNT index column at the very front
    df.insert(0, 'CH_COUNT', range(1, len(df) + 1)) 

    # 6. Save the intermediate CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Raw CSV saved to: {output_path.name}")

    # 7. Run your existing Kalman filter and CG acceleration translations
    print("Running Kalman filters and CG translations...")
    translate_linear_acc(str(output_path))
    process(str(output_path))
    
    print("🏎️ Pipeline Complete! Your data is fully processed.")

# ==========================================
# EXECUTION
# ==========================================
# Replace 'run_011.blf' with your actual CAN log file name!
process_can_log(
    log_filename='output_from_csv.blf', 
    dbc_filename='SDM26_Generated.dbc', 
    output_csv_name='final_telemetry.csv'
)