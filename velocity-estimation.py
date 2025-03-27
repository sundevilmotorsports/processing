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


def GPSProcessing( v_gps: np.ndarray[ float ] ) -> np.ndarray[ float ]:
    """
    Removes large outliers in GPS velocity data by replacing them by the previous value

    Args:
        v_gps ( np.ndarray[ float ] ): array of GPS velocity (m/s)

    Returns:
        v_gps_proc ( np.ndarray[ float ] ): array of processed GPS velocity (m/s)
    """
    # Remove large outliers from GPS velocity data
    v_gps_proc = np.zeros( v_gps.size )

    for i in range( v_gps.size ):
        if( v_gps[i] > 50 ):
            v_gps_proc[ i ] = v_gps_proc[ i - 1 ]
        else:
            v_gps_proc[ i ] = v_gps[ i ]
    
    return v_gps_proc


if __name__ == "__main__":

    df = pd.read_csv( "data120.csv" )

    time = df[ 'time (s)' ].to_numpy()
    ax_raw = df[ 'longitudinal accel (mG)' ].to_numpy()
    ay_raw = df[ 'lateral accel (mG)' ].to_numpy()
    w_fr = df[ 'fr wheel speed (rpm)' ].to_numpy()
    v_gps = df[ 'gps speed (m/s)' ].to_numpy()

    # Select mode for speed estimation:
    # 0 = IMU only ( open loop integration of Ax and Ay )
    # 1 = GPS only
    # 2 = Filtered Wheel Speed only
    # 3 = Fusion of Ax and Wheel Speed
    # 4 = Fusion of Ax and GPS
    # 5 = Fusion of Ax, Ay and GPS
    mode = 5

    match mode:
        case 0:
            ax_KF = KF( ax_raw, 0.1, 10000 )    # Kalman Filter Ax (mG)
            ay_KF = KF( ay_raw, 0.1, 10000 )    # Kalman Filter Ay (mG)
            
            # Vx (m/s): Integration of filtered Ax
            vx_int = np.zeros( time.size )
            for i in range( 1, time.size ):
                vx_int[ i ] =  vx_int[ i - 1 ] + ( ( ( time[ i ] - time[ i - 1 ] ) * ( ax_KF[ i ] / 1000 * 9.80665 ) ) )

            # Vy (m/s): Integration of filtered Ay
            vy_int = np.zeros( time.size )
            for i in range( 1, time.size ):
                vy_int[ i ] =  vy_int[ i - 1 ] + ( ( ( time[ i ] - time[ i - 1 ] ) * ( ay_KF[ i ] / 1000 * 9.80665 ) ) )

            plt.figure()
            plt.subplot( 1, 2, 1 )
            plt.plot( time, ax_raw, time, ax_KF )
            plt.title( 'Ax Filtering' )
            plt.legend( [ 'Raw', 'KF' ] )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Ax (mG)')
            plt.grid()
            plt.subplot( 1, 2, 2 )
            plt.plot( time, vx_int )
            plt.title( 'Ax From Vx Integration' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Vx (m/s)' )
            plt.grid()

            plt.figure()
            plt.subplot( 1, 2, 1 )
            plt.plot( time, ay_raw, time, ay_KF )
            plt.title( 'Ay Filtering' )
            plt.legend( [ 'Raw', 'KF' ] )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Ay (mG)')
            plt.grid()
            plt.subplot( 1, 2, 2 )
            plt.plot( time, vy_int )
            plt.title( 'Ay from Vy Integration' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Vy (m/s)' )
            plt.grid()
            plt.show()

        case 1:
            v_gps_proc = GPSProcessing( v_gps )
            plt.figure()
            plt.plot( time, v_gps_proc )
            plt.title( 'Velocity from GPS' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Velocity (m/s)' )
            plt.grid()
            plt.show()

        case 2:
            w_fr_KF = KF( w_fr, 0.1, 10000 )        # Filtered Wheel Speed
            plt.subplot( 1, 2, 1 )
            plt.plot( time, w_fr, time, w_fr_KF )
            plt.title( 'Front Wheel Speed Filtering' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Wheel Speed (rad/s)' )
            plt.legend( [ 'Raw', 'KF' ] )
            plt.grid()
            plt.subplot( 1, 2, 2 )
            plt.plot( time, ( w_fr_KF * pi * 0.4572 ) / 60 )
            plt.title( 'Velocity from Front Wheel Speed' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Velocity (m/s)' )
            plt.grid()
            plt.show()

        case 3: 
            v_ax_wfr = fusionAxW( time, ax_raw, w_fr, 1, 10 )   # Fusion of Ax and wheel speed
            plt.plot( time, v_ax_wfr )
            plt.title( 'Velocity from Fusion of Ax & Front Wheel Speed' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Velocity (m/s)' )
            plt.grid()
            plt.show()

        case 4: 
            v_gps_proc = GPSProcessing( v_gps )
            v_ax_gps = fusionAxGps( time, ax_raw, v_gps_proc, 10, 10000 )   # Fusion of Ax and GPS
            plt.plot( time, v_ax_gps )
            plt.title( 'Velocity from Fusion of Ax & GPS' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Velocity (m/s)' )
            plt.grid()
            plt.show()

        case 5:
            v_gps_proc = GPSProcessing( v_gps )
            vx_EKF, vy_EKF = EKFVxVy( time, ax_raw, ay_raw, v_gps_proc, 1, 100 )    # Vx Vy Extended Kalman Filter
            plt.figure()
            plt.subplot( 1, 2, 1 )
            plt.plot( time, vx_EKF )
            plt.title( 'Vx From Fusion of Ax, Ay & GPS (EKF)' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Vx (m/s)' )
            plt.grid()
            plt.subplot( 1, 2, 2 )
            plt.plot( time, vy_EKF )
            plt.title( 'Vy From Fusion of Ax, Ay & GPS (EKF)' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'Vy (m/s)' )
            plt.grid()
            
            plt.figure()
            plt.plot( time, np.sqrt( vx_EKF ** 2 + vy_EKF ** 2) )
            plt.title( 'Velocity from Estimated Vx and Vy' )
            plt.xlabel( 'Time (s)' )
            plt.ylabel( 'V (m/s)' )
            plt.grid()
            plt.show()