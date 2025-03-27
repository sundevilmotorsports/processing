import numpy as np
import pandas as pd
from math import pi
import matplotlib.pyplot as plt


def KF( raw_data: np.ndarray[ float ], Q: float, R: float ) -> np.ndarray[ float ]:
    """
    Function to filter single sensor measurements ( IMU Ax, Ay or wheel speeds ) using a linear Kalman Filter

    Args:
        raw_data ( np.array[ float ] ): array of raw values
        Q ( float ): process noise covariance
        R ( float ): meaurement noise covariance

    Returns:
        filtered_data ( np.array[ float ] ): array of filtered values
    """

    filtered_data = np.zeros( raw_data.size )

    # Initializa KF
    # Q = 0.1
    # R = 10000
    x_p = 0
    x_e = 0
    P_p = 0
    P_e = 0

    for k in range( raw_data.size ):
        # I - Prediction
        x_p = x_e           # State prediction
        P_p = P_e + Q       # Error covariance prediction
        y = x_p             # Output estimate

        # II - Correction
        L = P_p / ( P_p + R )                   # Kalman Gain
        x_e = x_p + L * ( raw_data[ k ] - y )   # State estimate update
        P_e = ( 1 - L ) * P_p                   # Error covariance estimate update

        filtered_data[ k ] = x_e

    return filtered_data


def fusionAxW( t: np.ndarray[ float ], ax: np.ndarray[ float ], w: np.ndarray[ float ], Q: float, R: float ):
    """
    Sensor Fusion of Ax and front wheel speed to estimate speed

    Args:
        t ( np.ndarray[ float ] ): array of time points
        ax ( np.ndarray[ float ] ): array of longitudinal acceleration Ax ( mG/s^2 )
        w ( np.ndarray[ float ] ): array of front wheel angular velocity ( rad/s )
        Q ( float ): process noise covariance
        R ( float ): meaurement noise covariance

    Returns:
        filtered_v ( np.ndarray[ float ] ): array of estimated velocity (m/s)
    """

    filtered_v = np.zeros( ax.size )

    # Plant Dyanamics C vector
    wheel_radius = 0.4572    # wheel radius in meters
    C = ( 60 / ( pi * wheel_radius ) )

    # Initializa KF
    x_p = 0
    x_e = 0
    P_p = 0
    P_e = 0
    
    for i in range( 1, ax.size ):

        dt = t[ i ] - t[ i - 1 ]

        # I - Prediction
        x_p = x_e + ( dt * ax[ i ] / 1000 * 9.80665 )       # State prediction
        P_p = P_e + Q                                       # Error covariance prediction
        y = C * x_p                                         # Output estimate

        # II - Correction
        L = ( P_p * C ) / ( C * P_p * C + R )       # Kalman Gain
        x_e = x_p + L * ( w[ i ] - y )              # State estimate update
        P_e = ( 1 - L * C ) * P_p                   # Error covariance estimate update

        filtered_v[ i ] = x_e

    return filtered_v


def fusionAxGps( t: np.ndarray[ float ], ax: np.ndarray[ float ], gps: np.ndarray[ float ],
                 Q: float, R: float ) -> np.ndarray[ float ]:
    """
    Sensor fusion of Ax and GPS velocity to estimate speed using a linear Kalman Filter

    Args:
        t ( np.ndarray[ float ] ): array of time points (s)
        ax ( np.ndarray[ float ] ): array of longitudinal acceleration Ax ( mG/s^2 )
        gps ( np.ndarray[ float ] ): array of GPS velocity (m/s)
        Q ( float ): process noise covariance
        R ( float ): meaurement noise covariance

    Returns:
        filtered_v ( np.ndarray[ float ] ): array of estimated velocity (m/s)
    """

    filtered_v = np.zeros( ax.size )

    # Initialize KF
    x_p = 0
    x_e = 0
    P_p = 0
    P_e = 0

    for i in range( 1, ax.size ):

        dt = t[ i ] - t[ i - 1 ]

        # I - Prediction
        x_p = x_e + ( dt * ax[ i ] / 1000 * 9.80665 )       # State prediction
        P_p = P_e + Q                                       # Error covariance prediction
        y = x_p                                             # Output estimate

        # II - Correction
        L = ( P_p ) / (  P_p + R )          # Kalman Gain
        x_e = x_p + L * ( gps[ i ] - y )    # State estimate update
        P_e = ( 1 - L ) * P_p                # Error covariance estimate update

        filtered_v[ i ] = x_e

    return filtered_v


def EKFVxVy( t: np.ndarray[ float ], ax: np.ndarray[ float ], ay: np.ndarray[ float ],
             gps: np.ndarray[ float ], Q: float, R: float ) -> tuple[ np.ndarray[ float ], np.ndarray[ float ] ]:
    """
    Sensor fusion of Ax, Ay and GPS speed to estimate Vx and Vy using an Extended Kalman Filter.

    Args:
        t ( np.ndarray[ float ] ): array of time points
        ax ( np.ndarray[ float ] ): array of longitudinal acceleration Ax ( m/s^2 )
        ay ( np.ndarray[ float ] ): array of lateral acceleration Ay ( m/s^2 )
        gps ( np.ndarray[ float ] ): array of GPS velocity ( m/s )
        Q ( float ): process noise covariance
        R ( float ): meaurement noise covariance

    Returns:
        filtered_Vx ( np.ndarray[ float ] ): array of estimated longitudinal velocity Vx ( m/s )
        filtered_Vy ( np.ndarray[ float ] ): array of estimated latreral velocity Vy ( m/s )
    """

    filtered_Vx = np.zeros( t.size )
    filtered_Vy = np.zeros( t.size )

    # State Space
    A = np.array( [ [ 1, 0 ], [ 0, 1 ] ] )      # A matrix
    H = np.zeros( ( 1, 2 ) )                    # Jacobian of the measurement
    u = np.zeros( ( 2, 1 ) )                    # Input vector

    # Initializa KF
    Q = np.eye( 2 ) * Q
    x_p = np.zeros( ( 2, 1 ) )
    x_e = np.zeros( ( 2, 1 ) )
    P_p = np.eye( 2 )
    P_e = np.eye( 2 )
    I = np.eye( 2 )

    for k in range( 1, t.size ):

        dt = t[ k ] - t[ k - 1 ]
        B = np.array( [ [ dt * 9.80665 / 1000 , 0 ], [ 0, dt * 9.80665 / 1000 ] ] )     # State-space B matrix
        u = np.array( [ [ ax[ k ] ], [ ay[ k ] ] ] )            # Input vector

        # I - Prediction
        x_p = ( A @ x_e ) + ( B @ u )       # State prediction
        P_p = ( A @ P_e @ A.T ) + Q         # Error covariance prediction

        Vx = x_e[ 0 ][ 0 ]
        Vy = x_e[ 1 ][ 0 ]

        if Vx == 0:
            H[ 0 ][ 0 ] = 0
        else:
            H[ 0 ][ 0 ] = Vx / np.sqrt( Vx ** 2 + Vy ** 2)

        if Vy == 0:
            H[ 0 ][ 1 ] = 0
        else:
            H[ 0 ][ 1 ] = Vy / np.sqrt( Vx ** 2 + Vy ** 2)

        y = H @ x_p                          # Output estimate

        # II - Correction
        L = ( P_p @ H.T ) / ( ( H @ P_p @ H.T ) + R )   # Kalman Gain
        x_e = x_p + L @ ( gps[ k ] - y )                # State estimate update
        P_e = ( I - L @ H ) @ P_p                       # Error covariance estimate update

        filtered_Vx[ k ] = x_e[ 0 ][ 0 ]
        filtered_Vy[ k ] = x_e[ 1 ][ 0 ] 

    return filtered_Vx, filtered_Vy


if __name__ == "__main__":

    ## LOAD DATA
    df = pd.read_csv( "data120.csv" )

    time = df[ 'time (s)' ].to_numpy()
    ax_raw = df[ 'longitudinal accel (mG)' ].to_numpy()
    ay_raw = df[ 'lateral accel (mG)' ].to_numpy()
    w_fl = df[ 'fl wheel speed (rpm)' ].to_numpy()
    w_fr = df[ 'fr wheel speed (rpm)' ].to_numpy()
    v_gps = df[ 'gps speed (m/s)' ].to_numpy()

    ## DATA PROCESSING
    # Kalman Filter Ax (mG)
    ax_KF = KF( ax_raw, 0.1, 10000 )   

    # Kalman Filter Ay (mG)
    ay_KF = KF( ay_raw, 0.1, 10000 )

    # Vx (m/s): Integration of filtered Ax
    vx_int = np.zeros( time.size )
    for i in range( 1, time.size ):
        vx_int[ i ] =  vx_int[ i - 1 ] + ( ( ( time[ i ] - time[ i - 1 ] ) * ( ax_KF[ i ] / 1000 * 9.80665 ) ) )

    # Vy (m/s): Integration of filtered Ay
    vy_int = np.zeros( time.size )
    for i in range( 1, time.size ):
        vy_int[ i ] =  vy_int[ i - 1 ] + ( ( ( time[ i ] - time[ i - 1 ] ) * ( ay_KF[ i ] / 1000 * 9.80665 ) ) )

    # Remove large outliers from GPS velocity data
    v_gps_proc = np.zeros( v_gps.size )
    for i in range( v_gps.size ):
        if( v_gps[i] > 100 ):
            v_gps_proc[i] = v_gps_proc[ i - 1 ]
        else:
            v_gps_proc[i] = v_gps[i]

    # Filtered Wheel Speed
    w_fr_KF = KF( w_fr, 0.1, 10000 )

    # Vx: fusion of Ax and wheel speed
    v_ax_wfr = fusionAxW( time, ax_raw, w_fr, 1, 10 )

    # Vx: fusion of Ax and gps
    v_ax_gps = fusionAxGps( time, ax_raw, v_gps_proc, 10, 10000 )

    # Vx Vy Extended Kalman Filter
    vx_EKF, vy_EKF = EKFVxVy( time, ax_raw, ay_raw, v_gps_proc, 1, 100 )

    ## PLOTS
    # Ax filtering
    plt.figure()
    plt.plot( time, ax_raw, time, ax_KF )
    plt.grid()
    plt.title( 'Ax Filtering' )
    plt.legend( [ 'Raw', 'KF' ] )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Ax (mG)')

    # Ay
    plt.figure()
    plt.plot( time, ay_raw, time, ay_KF )
    plt.grid()
    plt.title( 'Ay Filtering' )
    plt.legend( [ 'Raw', 'KF' ] )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Ay (mG)')

    # Vx integration
    plt.figure()
    plt.plot( time, vx_int )
    plt.grid()
    plt.title( 'Vx Integration' )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Vx (m/s)' )

    # Vy integration
    plt.figure()
    plt.plot( time, vy_int )
    plt.grid()
    plt.title( 'Vy Integration' )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Vy (m/s)' )

    plt.figure()
    plt.plot( time, vx_EKF )
    plt.grid()
    plt.title( 'Vx EKF' )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Vx (m/s)' )

    plt.figure()
    plt.plot( time, vy_EKF )
    plt.grid()
    plt.title( 'Vy EKF' )
    plt.xlabel( 'Time (s)' )
    plt.ylabel( 'Vy ( m/s )' )

    # Filtered Wheel speed
    plt.figure()
    plt.plot( time, w_fr, time, w_fr_KF )
    plt.grid()
    plt.title( "Wheel Speed Filtering" )
    plt.legend( [ 'Raw', 'KF' ] )

    plt.figure()
    # plt.plot(  time, v_gps_proc, time, v_ax_wfr, time, ( w_fr_KF * pi * 0.4572 ) / 60, time, v_ax_gps )
    plt.plot(  time, v_gps_proc, time, v_ax_gps )
    plt.grid()
    plt.title( 'Velocity' )
    plt.legend( [ 'GPS', 'Fusion Ax-GPS' ] )
    
    plt.show()
