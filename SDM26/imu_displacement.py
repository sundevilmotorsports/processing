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

    t = df[ 'TS' ].to_numpy()
    ax_IMU = df[ 'IMU_X_ACCEL' ].to_numpy() / 1000      # convert from mg to g
    ay_IMU = df[ 'IMU_Y_ACCEL' ].to_numpy() / 1000      # convert from mg to g
    az_IMU = df[ 'IMU_Z_ACCEL' ].to_numpy() / 1000      # convert from mg to g
    gz = df[ 'IMU_Z_GYRO' ].to_numpy() / 1000           # convert from mdps to dps

    # IMU x coordinate in meters (to be adjusted based on SDM25, SDM26)
    x_IMU = 0.5

    # Linear x acceleration correction
    ax_CG = ax_IMU + ( ( gz ** 2 ) * x_IMU )

    # Yaw derivative
    dt_gz = np.zeros_like( gz )

    for i in range( 1, len( gz ) ):
         dt_gz[ i ] = ( gz[ i ] - gz[ i - 1 ] ) / ( t[ i ] - t[ i - 1 ] )  

    # Linear y acceleration correction
    ay_CG = ay_IMU - ( dt_gz * x_IMU )

    # Insert new columns after IMU_Z_GYRO
    index = df.columns.get_loc( 'IMU_Z_GYRO' ) + 1
    
    df.insert( loc=index, column='CG_X_ACCEL', value=ax_CG * 1000 )   # convert back to mg
    df.insert( loc=index+1, column='CG_Y_ACCEL', value=ay_CG * 1000 )   # convert back to mg
    df.insert( loc=index+2, column='CG_Z_ACCEL', value=az_IMU * 1000 )   # convert back to mg
    
    df.to_csv( csv_file )