import numpy as np
import pandas as pd

def translate_linear_acc( csv_file: str ) :
    """Translates IMU linear acceleration data from IMU frame to CG and adds the data in 3 new columns to the csv file.
       - CG_X_ACCEL
       - CG_Y_ACCEL
       - CG_Z_ACCEL

       This function assumes the following:
       - the IMU is only offset in the x direction from the CG.
       - the vehicle moves in the x-y plane only (no roll or pitch).

       The equations are from: 
       https://basicairdata.eu/knowledge-center/compensation/inertial-measurement-unit-placement/

    Args:
        csv_file (str): Path to the CSV file 
    """
    df = pd.read_csv( csv_file )
    df['TS_ROUNDED'] = df['TS'].round(5)
    df = df.drop_duplicates(subset="TS_ROUNDED")
    df = df.sort_values("TS_ROUNDED").drop(columns=['TS_ROUNDED'])

    t = df[ 'TS' ].to_numpy()

    # --- FIX GYRO SCALING (mdps → dps) ---
    df["IMU_X_GYRO"] = df["IMU_X_GYRO"] / 1000.0
    df["IMU_Y_GYRO"] = df["IMU_Y_GYRO"] / 1000.0
    df["IMU_Z_GYRO"] = df["IMU_Z_GYRO"] / 1000.0

    # Opted to Output CSV in G rather than mG
    ax_IMU = df[ 'IMU_X_ACCEL' ].to_numpy()             # convert from mg to g
    ay_IMU = df[ 'IMU_Y_ACCEL' ].to_numpy()             # convert from mg to g
    az_IMU = df[ 'IMU_Z_ACCEL' ].to_numpy()             # convert from mg to g
    gz = df[ 'IMU_Z_GYRO' ].to_numpy()                  # convert from mdps to dps
    gz = np.deg2rad(gz)                                 # convert from dps to rps

    gz_smoothed = pd.Series(gz).rolling(window=5, center=True).mean().bfill().ffill().to_numpy()

    # IMU x coordinate in meters (to be adjusted based on SDM25, SDM26)
    x_IMU = 0.5

    # Linear x acceleration correction
    ax_CG = ax_IMU + ( ( gz_smoothed ** 2 ) * x_IMU ) / 9.81

    # Yaw derivative
    dt_gz = np.zeros_like(gz)

    for i in range(1, len(gz)):
        dt = t[i] - t[i - 1]

        # Guard against bad timestamps
        if dt <= 1e-4 or np.isnan(dt):
            dt_gz[i] = 0
            continue

    # Linear y acceleration correction
    ay_CG = ay_IMU - ( dt_gz * x_IMU ) / 9.81
    
    for col, val in zip(['CG_X_ACCEL', 'CG_Y_ACCEL', 'CG_Z_ACCEL'], [ax_CG, ay_CG, az_IMU]):
        if col in df.columns:
            df[col] = val # convert back to mg
        else:
            index = df.columns.get_loc('IMU_Z_GYRO') + 1
            df.insert(loc=index, column=col, value=val)
    
    df.to_csv( csv_file , index=False)