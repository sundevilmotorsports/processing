from typing import List, Tuple, Callable

class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: Callable | float = 1.0
    signed: bool = False
    byte_order: str = "little"
    units: str = ""
    display_name: str = ""
    short_name: str = ""

    def __init__(self, name: str, column_index: int, byte_size: int,
                 conversion_factor: Callable | float = 1.0,
                 signed: bool = False,
                 byte_order: str = "little",
                 units: str = "",
                 display_name: str = "",
                 short_name: str = ""):
        self.name = name
        self.column_index = column_index
        self.byte_size = byte_size
        self.conversion_factor = conversion_factor
        self.signed = signed
        self.byte_order = byte_order
        self.units = units
        self.display_name = display_name if display_name else name
        self.short_name = short_name if short_name else name[:8]

    def getData(self, data: bytes):
        value = int.from_bytes(data, byteorder=self.byte_order, signed=self.signed)
        if callable(self.conversion_factor):
            return self.conversion_factor(value)
        return value * self.conversion_factor


def create_devices(device_names: List[str], data_sizes: List[int]) -> List[device_data]:
    return [device_data(name.strip(), i, data_sizes[i]) for i, name in enumerate(device_names)]


def configure_devices(devices: List[device_data]) -> None:
    """
    Apply per-device conversion_factor, signed flags, units, and display names in a single place.
    Call this after creating devices so all files share the same rules.
    """
    for device in devices:
        name = device.name
        # Keep these rules in sync with your other files
        match name:
            case "TS":
                device.conversion_factor = 1e-6
                device.units = "s"
                device.display_name = "Time"
                device.short_name = "Time"
            case "F_BRAKEPRESSURE":
                device.units = "kPa"
                device.display_name = "Front Brake Pressure"
                device.short_name = "F_BrkPrs"
            case "R_BRAKEPRESSURE":
                device.units = "kPa"
                device.display_name = "Rear Brake Pressure"
                device.short_name = "R_BrkPrs"
            case "STEERING":
                device.conversion_factor = lambda v: ((0.084769) * ( (v) - (1783) ) )
                device.units = "deg"
                device.display_name = "Steering"
                device.short_name = "Steering"
            case "FLSHOCK":
                device.conversion_factor = lambda v: ((-0.018586) * ( (v) - (1311) ) ) # Change the value added to (v) to move zero
                device.units = "mm"
                device.display_name = "FL Shock"
                device.short_name = "FL_Shock"
            case "FRSHOCK":
                device.conversion_factor = lambda v: ((-0.018444) * ( (v) - (1324) ) )
                device.units = "mm"
                device.display_name = "FR Shock"
                device.short_name = "FR_Shock"
            case "RRSHOCK":
                device.conversion_factor = lambda v: ((-0.018498) * ( (v) - (1370) ) )
                device.units = "mm"
                device.display_name = "RR Shock"
                device.short_name = "RR_Shock"
            case "RLSHOCK":
                device.conversion_factor = lambda v: ((-0.018600) * ( (v) - (1403) ) )
                device.units = "mm"
                device.display_name = "RL Shock"
                device.short_name = "RL_Shock"
            case "CURRENT":
                device.conversion_factor = 1.25
                device.signed = True
                device.units = "A"
                device.display_name = "Current"
                device.short_name = "Current"
            case "BATTERY":
                device.conversion_factor = 1.25 / 1000
                device.signed = True
                device.units = "V"
                device.display_name = "Battery Voltage"
                device.short_name = "Battery"
            case "IMU_X_ACCEL":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) / 1000
                device.units = "G"
                device.display_name = "IMU X Accel"
                device.short_name = "IMU_X"
            case "IMU_Y_ACCEL":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) / 1000
                device.units = "G"
                device.display_name = "IMU Y Accel"
                device.short_name = "IMU_Y"
            case "IMU_Z_ACCEL":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) / 1000
                device.units = "G"
                device.display_name = "IMU Z Accel"
                device.short_name = "IMU_Z"
            case "IMU_X_GYRO":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.50)
                device.units = "deg/s"
                device.display_name = "IMU X Gyro"
                device.short_name = "Gyro_X"
            case "IMU_Y_GYRO":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.50)
                device.units = "deg/s"
                device.display_name = "IMU Y Gyro"
                device.short_name = "Gyro_Y"
            case "IMU_Z_GYRO":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.50)
                device.units = "deg/s"
                device.display_name = "IMU Z Gyro"
                device.short_name = "Gyro_Z"
            case "FR_SG":
                device.conversion_factor = lambda v: (v)
                device.units = "raw"
                device.display_name = "FR Strain Gauge"
                device.short_name = "FR_SG"
            case "FL_SG":
                device.conversion_factor = lambda v: (-11052026.1 * v + 2606.22253)
                device.units = "raw"
                device.display_name = "FL Strain Gauge"
                device.short_name = "FL_SG"
            case "RL_SG":
                device.conversion_factor = lambda v: (-1401922.44 * v + 92026.0137)
                device.units = "raw"
                device.display_name = "RL Strain Gauge"
                device.short_name = "RL_SG"
            case "RR_SG":
                device.conversion_factor = lambda v: (v)
                device.units = "raw"
                device.display_name = "RR Strain Gauge"
                device.short_name = "RR_SG"
            case "FLW_AMB":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "C"
                device.display_name = "FL Wheel Ambient"
                device.short_name = "FLW_Amb"
            case "FLW_OBJ":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "raw"
                device.display_name = "FL Wheel Object"
                device.short_name = "FLW_Obj"
            case "FLW_RPM":
                device.units = "rpm"
                device.display_name = "FL Wheel RPM"
                device.short_name = "FLW_RPM"
            case "FRW_AMB":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "C"
                device.display_name = "FR Wheel Ambient"
                device.short_name = "FRW_Amb"
            case "FRW_OBJ":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "raw"
                device.display_name = "FR Wheel Object"
                device.short_name = "FRW_Obj"
            case "FRW_RPM":
                device.units = "rpm"
                device.display_name = "FR Wheel RPM"
                device.short_name = "FRW_RPM"
            case "RRW_AMB":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "C"
                device.display_name = "RR Wheel Ambient"
                device.short_name = "RRW_Amb"
            case "RRW_OBJ":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "raw"
                device.display_name = "RR Wheel Object"
                device.short_name = "RRW_Obj"
            case "RRW_RPM":
                device.units = "rpm"
                device.display_name = "RR Wheel RPM"
                device.short_name = "RRW_RPM"
            case "RLW_AMB":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "C"
                device.display_name = "RL Wheel Ambient"
                device.short_name = "RLW_Amb"
            case "RLW_OBJ":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15) / 1000
                device.units = "raw"
                device.display_name = "RL Wheel Object"
                device.short_name = "RLW_Obj"
            case "RLW_RPM":
                device.units = "rpm"
                device.display_name = "RL Wheel RPM"
                device.short_name = "RLW_RPM"
            case "BRAKE_FLUID":
                device.units = "raw"
                device.display_name = "Brake Fluid"
                device.short_name = "BrkFluid"
            case "THROTTLE_LOAD":
                device.units = "%"
                device.display_name = "Throttle Load"
                device.short_name = "Throttle"
            case "BRAKE_LOAD":
                device.units = "%"
                device.display_name = "Brake Load"
                device.short_name = "Brake"
            case "DRS":
                device.units = "bool"
                device.display_name = "DRS"
                device.short_name = "DRS"
            case "GPS_LON":
                device.units = "deg"
                device.display_name = "GPS Longitude"
                device.short_name = "GPS_Lon"
            case "GPS_LAT":
                device.units = "deg"
                device.display_name = "GPS Latitude"
                device.short_name = "GPS_Lat"
            case "GPS_SPD":
                device.units = "kph"
                device.display_name = "GPS Speed"
                device.short_name = "GPS_Spd"
            case "GPS_FIX":
                device.units = "bool"
                device.display_name = "GPS Fix"
                device.short_name = "GPS_Fix"
            case "ENGINE_SPEED":
                device.conversion_factor = lambda v: v
                device.units = "rpm"
                device.display_name = "Engine Speed"
                device.short_name = "Eng_Spd"

            case "ECT":
                device.conversion_factor = lambda v: v - 50
                device.units = "deg C"
                device.display_name = "Engine Coolant Temp"
                device.short_name = "ECT"

            case "OIL_TEMP":
                device.conversion_factor = lambda v: v - 50
                device.units = "deg C"
                device.display_name = "Engine Oil Temp"
                device.short_name = "Oil_Tmp"

            case "OIL_PRESS":
                device.conversion_factor = lambda v: v
                device.units = "kPa"
                device.display_name = "Oil Pressure"
                device.short_name = "Oil_Prs"

            case "NEUTRAL_STAT":
                device.conversion_factor = lambda v: v
                device.units = ""
                device.display_name = "Neutral Status"
                device.short_name = "Neutral_Stat"

            case "LAMBDA":
                device.conversion_factor = lambda v: 0.01 * v
                device.units = "Lambda"
                device.display_name = "Lambda 1"
                device.short_name = "Lambda"

            case "TPS":
                device.conversion_factor = lambda v: v
                device.units = "%"
                device.display_name = "Throttle Position"
                device.short_name = "TPS"

            case "GEAR":
                device.conversion_factor = lambda v: v
                device.units = ""
                device.display_name = "Gear Position"
                device.short_name = "Gear_Pos"

            case "GP_SPEED":
                device.conversion_factor = lambda v: 0.1 * v
                device.units = "km/h"
                device.display_name = "Vehicle Speed"
                device.short_name = "VSS"

            case "APS_MAIN":
                device.conversion_factor = lambda v: 0.1 * v
                device.units = "%"
                device.display_name = "APS Main"
                device.short_name = "APS"

            case "FUEL_PRESS":
                device.conversion_factor = lambda v: v
                device.units = "kPa"
                device.display_name = "Fuel Pressure"
                device.short_name = "Fuel_Prs"

            case "ACCEL_FUEL":
                device.conversion_factor = lambda v: 0.001 * v
                device.units = "ms"
                device.display_name = "Accel Fuel"
                device.short_name = "Accel_Fuel"

            case "ACCUM_DIST":
                device.conversion_factor = lambda v: 0.1 * v
                device.units = "km"
                device.display_name = "Accumulated Distance"
                device.short_name = "Accum_Dist"

            case "MAP":
                device.conversion_factor = lambda v: v
                device.units = "kPa"
                device.display_name = "Manifold Pressure"
                device.short_name = "MAP"

            case "AN_TEMP_3_":
                device.conversion_factor = lambda v: v - 50
                device.units = "deg C"
                device.display_name = "AN Temp 3"
                device.short_name = "AN_T3"

            case "ENG_IMU_X":
                device.conversion_factor = lambda v: (((v - 65536) if v >= 32768 else v) * 0.001)
                device.units = "g"
                device.display_name = "ECU Lateral Accel"
                device.short_name = "G_Lat"

            case "ENG_IMU_Y":
                device.conversion_factor = lambda v: (((v - 65536) if v >= 32768 else v) * 0.001)
                device.units = "g"
                device.display_name = "ECU Longitudinal Accel"
                device.short_name = "G_Long"

            case "ENG_IMU_Z":
                device.conversion_factor = lambda v: (((v - 65536) if v >= 32768 else v) * 0.001)
                device.units = "g"
                device.display_name = "ECU Vertical Accel"
                device.short_name = "G_Vert"
            case "TESTNO":
                device.units = "num"
                device.display_name = "Test Number"
                device.short_name = "TestNo"
            case "DTC_FLW":
                device.units = "code"
                device.display_name = "DTC FL Wheel"
                device.short_name = "DTC_FLW"
            case "DTC_FRW":
                device.units = "code"
                device.display_name = "DTC FR Wheel"
                device.short_name = "DTC_FRW"
            case "DTC_RLW":
                device.units = "code"
                device.display_name = "DTC RL Wheel"
                device.short_name = "DTC_RLW"
            case "DTC_RRW":
                device.units = "code"
                device.display_name = "DTC RR Wheel"
                device.short_name = "DTC_RRW"
            case "DTC_FLSG":
                device.units = "code"
                device.display_name = "DTC FL Strain"
                device.short_name = "DTC_FLSG"
            case "DTC_FRSG":
                device.units = "code"
                device.display_name = "DTC FR Strain"
                device.short_name = "DTC_FRSG"
            case "DTC_RLSG":
                device.units = "code"
                device.display_name = "DTC RL Strain"
                device.short_name = "DTC_RLSG"
            case "DTC_RRSG":
                device.units = "code"
                device.display_name = "DTC RR Strain"
                device.short_name = "DTC_RRSG"
            case "DTC_IMU":
                device.units = "code"
                device.display_name = "DTC IMU"
                device.short_name = "DTC_IMU"
            case "GPS_0_":
                device.units = "raw"
                device.display_name = "GPS 0"
                device.short_name = "GPS_0"
            case "GPS_1_":
                device.units = "raw"
                device.display_name = "GPS 1"
                device.short_name = "GPS_1"
            case "CH_COUNT":
                device.units = "num"
                device.display_name = "Channel Count"
                device.short_name = "CH_Count"
            case "FR_Wheel_Speed":
                device.units = "kph"
                device.display_name = "FR Wheel Speed"
                device.short_name = "FR_wspd"
            case "FL_Wheel_Speed":
                device.units = "kph"
                device.display_name = "FL Wheel Speed"
                device.short_name = "FL_wspd"

            # Old WFT Handlers
            # case "SLIP_ANG_1_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 1"
            #     device.short_name = "SlipAng1"
            # case "SLIP_ANG_2_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 2"
            #     device.short_name = "SlipAng2"
            # case "SLIP_ANG_3_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 3"
            #     device.short_name = "SlipAng3"
            # case "SLIP_ANG_4_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 4"
            #     device.short_name = "SlipAng4"
            # case "SLIP_ANG_5_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 5"
            #     device.short_name = "SlipAng5"
            # case "SLIP_ANG_6_":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0013733329264) * (v))
            #     device.units = "deg"
            #     device.display_name = "Slip Angle 6"
            #     device.short_name = "SlipAng6"
            # case "LR_X_Force":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.274424979248047) * (v))
            #     device.units = "lbf"
            #     device.display_name = "LR X Force"
            #     device.short_name = "LR_FX"
            # case "LR_Y_Force":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.137212489624023) * (v))
            #     device.units = "lbf"
            #     device.display_name = "LR Y Force"
            #     device.short_name = "LR_FY"
            # case "LR_Z_Force":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.274424979248047) * (v))
            #     device.units = "lbf"
            #     device.display_name = "LR Z Force"
            #     device.short_name = "LR_FZ"
            # case "LR_MX_Moment":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.135051663024902) * (v))
            #     device.units = "lb-ft"
            #     device.display_name = "LR MX Moment"
            #     device.short_name = "LR_MX"
            # case "LR_MY_Moment":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.135051663024902) * (v))
            #     device.units = "lb-ft"
            #     device.display_name = "LR MY Moment"
            #     device.short_name = "LR_MY"
            # case "LR_MZ_Moment":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.135051663024902) * (v))
            #     device.units = "lb-ft"
            #     device.display_name = "LR MZ Moment"
            #     device.short_name = "LR_MZ"
            # case "LR_Velocity":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.06103515625) * (v))
            #     device.units = "rpm"
            #     device.display_name = "LR Velocity"
            #     device.short_name = "LR_Vel"
            # case "LR_Position":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.010986328125) * (v))
            #     device.units = "deg"
            #     device.display_name = "LR Position"
            #     device.short_name = "LR_Pos"
            # case "LR_X_Acceleration":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0030517578125) * (v))
            #     device.units = "G"
            #     device.display_name = "LR X Acceleration"
            #     device.short_name = "LR_AX"
            # case "LR_Y_Acceleration":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0030517578125) * (v))
            #     device.units = "G"
            #     device.display_name = "LR Y Acceleration"
            #     device.short_name = "LR_AY"
            # case "LR_Z_Acceleration":
            #     device.signed = True
            #     device.conversion_factor = lambda v: ((0.0030517578125) * (v))
            #     device.units = "G"
            #     device.display_name = "LR Z Acceleration"
            #     device.short_name = "LR_AZ"


def generate_channel_list(devices: List[device_data]) -> List[Tuple[str, str, str, str]]:
    """
    Generate a channel list in the format required by CSV-to-MoTeC conversion.
    Returns: List of (csv_header_name, display_name, short_name, units) tuples
    """
    return [
        (device.name, device.display_name, device.short_name, device.units)
        for device in devices
    ]
