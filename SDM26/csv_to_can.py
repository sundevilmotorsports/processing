import pandas as pd
import can
import cantools
from pathlib import Path

def convert_csv_to_blf(csv_filename, dbc_filename, output_blf_name):
    # 1. Setup file paths
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / csv_filename
    dbc_path = script_dir / dbc_filename
    output_path = script_dir / output_blf_name

    if not csv_path.exists():
        print(f"❌ ERROR: Cannot find CSV at {csv_path}")
        return
    if not dbc_path.exists():
        print(f"❌ ERROR: Cannot find DBC at {dbc_path}")
        return

    # 2. Load DBC and CSV
    print(f"Loading DBC: {dbc_path.name}...")
    db = cantools.database.load_file(str(dbc_path))

    print(f"Loading CSV: {csv_path.name}...")
    df = pd.read_csv(str(csv_path))
    
    # Fill any empty cells (NaNs) with 0 so the encoder doesn't crash
    df = df.fillna(0)

    print(f"Encoding {len(df)} rows into binary CAN data... This might take a few seconds.")

    # 3. Create the BLF Writer
    with can.BLFWriter(str(output_path)) as writer:
        for idx, row in df.iterrows():
            ts = row.get('TS', idx * 0.01) # Grab timestamp, default to fake time if missing

            # Helper function to safely encode and write a single CAN message
            def send_msg(msg_name, data_dict):
                try:
                    msg = db.get_message_by_name(msg_name)
                    # strict=False allows the encoder to gracefully clamp floats that slightly exceed limits
                    data = msg.encode(data_dict, strict=False) 
                    writer.on_message_received(can.Message(
                        timestamp=ts,
                        arbitration_id=msg.frame_id,
                        data=data,
                        is_extended_id=False
                    ))
                except Exception as e:
                    pass # Silently skip if the math overflows

            # ==========================================
            # 4. Map CSV rows back to DBC messages
            # ==========================================

            # IMU Sensors
            if 'IMU_X_ACCEL' in df.columns:
                send_msg('IMU_ACCEL', {
                    'IMU_ACCEL_X': row['IMU_X_ACCEL'], 'IMU_ACCEL_Y': row['IMU_Y_ACCEL'], 'IMU_ACCEL_Z': row['IMU_Z_ACCEL']
                })
            if 'IMU_X_GYRO' in df.columns:
                send_msg('IMU_GYRO', {
                    'IMU_GYRO_X': row['IMU_X_GYRO'], 'IMU_GYRO_Y': row['IMU_Y_GYRO'], 'IMU_GYRO_Z': row['IMU_Z_GYRO']
                })

            # Wheel Boards
            if 'FLW_RPM' in df.columns:
                send_msg('FLWB', {'FLWB_rpm': row['FLW_RPM'], 'FLWB_ObjTemp': row['FLW_OBJ'], 'FLWB_AmbTemp': row['FLW_AMB']})
            if 'FRW_RPM' in df.columns:
                send_msg('FRWB', {'FRWB_rpm': row['FRW_RPM'], 'FRWB_ObjTemp': row['FRW_OBJ'], 'FRWB_AmbTemp': row['FRW_AMB']})
            if 'RLW_RPM' in df.columns:
                send_msg('RLWB', {'RLWB_rpm': row['RLW_RPM'], 'RLWB_ObjTemp': row['RLW_OBJ'], 'RLWB_AmbTemp': row['RLW_AMB']})
            if 'RRW_RPM' in df.columns:
                send_msg('RRWB', {'RRWB_rpm': row['RRW_RPM'], 'RRWB_ObjTemp': row['RRW_OBJ'], 'RRWB_AmbTemp': row['RRW_AMB']})

            # Strain Gauges
            if 'FL_SG' in df.columns: send_msg('FLSG', {'FLSG_Strain': row['FL_SG']})
            if 'FR_SG' in df.columns: send_msg('FRSG', {'FRSG_Strain': row['FR_SG']})
            if 'RL_SG' in df.columns: send_msg('RLSG', {'RLSG_Strain': row['RL_SG']})
            if 'RR_SG' in df.columns: send_msg('RRSG', {'RRSG_Strain': row['RR_SG']})

            # Steering & Shocks
            if 'STEERING' in df.columns:
                send_msg('STEERING_DATA', {'STEERING': row['STEERING']})
            if 'FLSHOCK' in df.columns:
                send_msg('SHOCK_DATA', {
                    'FLSHOCK': row['FLSHOCK'], 'FRSHOCK': row['FRSHOCK'],
                    'RLSHOCK': row['RLSHOCK'], 'RRSHOCK': row['RRSHOCK']
                })

            # Engine (Multiplexed - split into 3 separate CAN frames!)
            if 'ECT' in df.columns:
                send_msg('ENGINE', {
                    'ENGINE_Mux': 0, 'ENGINE_ect': row['ECT'], 'ENGINE_OilPressure': row.get('OIL_PSR', 0),
                    'ENGINE_Speed': 0, 'ENGINE_OilTemp': 0
                })
            if 'TPS' in df.columns:
                send_msg('ENGINE', {
                    'ENGINE_Mux': 1, 'ENGINE_tps': row['TPS'], 'ENGINE_Driven_wspd': row.get('DRIVEN_WSPD', 0)
                })
            if 'APS' in df.columns:
                send_msg('ENGINE', {
                    'ENGINE_Mux': 2, 'ENGINE_aps': row['APS']
                })

    print(f"✅ Successfully converted CSV back to a raw CAN file: {output_path.name}")

# ==========================================
# EXECUTION
# ==========================================
convert_csv_to_blf(
    csv_filename='processed/test_02_21/gen_testing_kaden_11_23_011.csv', 
    dbc_filename='SDM26_Generated.dbc', 
    output_blf_name='output_from_csv.blf'
)