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
    Apply per-device conversion_factor, signed flags, units, and display names dynamically from DBC.
    """
    for device in devices:
        match device.name:
            case "ENGINE_Mux":
                device.display_name = "ENGINE Mux"
                device.short_name = "ENGINE_M"
            case "ENGINE_aps":
                device.signed = True
                device.display_name = "ENGINE aps"
                device.short_name = "ENGINE_a"
            case "ENGINE_Speed":
                device.display_name = "ENGINE Speed"
                device.short_name = "ENGINE_S"
            case "ENGINE_tps":
                device.signed = True
                device.display_name = "ENGINE tps"
                device.short_name = "ENGINE_t"
            case "ENGINE_ect":
                device.signed = True
                device.display_name = "ENGINE ect"
                device.short_name = "ENGINE_e"
            case "ENGINE_Driven_wspd":
                device.display_name = "ENGINE Driven wspd"
                device.short_name = "ENGINE_D"
            case "ENGINE_OilTemp":
                device.signed = True
                device.display_name = "ENGINE OilTemp"
                device.short_name = "ENGINE_O"
            case "ENGINE_OilPressure":
                device.signed = True
                device.display_name = "ENGINE OilPressure"
                device.short_name = "ENGINE_O"
            case "SHIFTER_Shift0":
                device.signed = True
                device.display_name = "SHIFTER Shift0"
                device.short_name = "SHIFTER_"
            case "SHIFTER_Shift1":
                device.signed = True
                device.display_name = "SHIFTER Shift1"
                device.short_name = "SHIFTER_"
            case "SHIFTER_Shift2":
                device.signed = True
                device.display_name = "SHIFTER Shift2"
                device.short_name = "SHIFTER_"
            case "RLSG_Strain":
                device.signed = True
                device.display_name = "RLSG Strain"
                device.short_name = "RLSG_Str"
            case "RRSG_Strain":
                device.signed = True
                device.display_name = "RRSG Strain"
                device.short_name = "RRSG_Str"
            case "FRSG_Strain":
                device.signed = True
                device.display_name = "FRSG Strain"
                device.short_name = "FRSG_Str"
            case "FLSG_Strain":
                device.display_name = "FLSG Strain"
                device.short_name = "FLSG_Str"
            case "RLWB_rpm":
                device.units = "rpm"
                device.display_name = "RLWB rpm"
                device.short_name = "RLWB_rpm"
            case "RLWB_ObjTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "RLWB ObjTemp"
                device.short_name = "RLWB_Obj"
            case "RLWB_AmbTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "RLWB AmbTemp"
                device.short_name = "RLWB_Amb"
            case "RRWB_rpm":
                device.units = "rpm"
                device.display_name = "RRWB rpm"
                device.short_name = "RRWB_rpm"
            case "RRWB_ObjTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "RRWB ObjTemp"
                device.short_name = "RRWB_Obj"
            case "RRWB_AmbTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "RRWB AmbTemp"
                device.short_name = "RRWB_Amb"
            case "FRWB_rpm":
                device.units = "rpm"
                device.display_name = "FRWB rpm"
                device.short_name = "FRWB_rpm"
            case "FRWB_ObjTemp":
                device.conversion_factor = lambda v: (v * 0.02) + (-273.15)
                device.units = "°C"
                device.display_name = "FRWB ObjTemp"
                device.short_name = "FRWB_Obj"
            case "FRWB_AmbTemp":
                device.conversion_factor = lambda v: (v * 0.02) + (-273.15)
                device.units = "°C"
                device.display_name = "FRWB AmbTemp"
                device.short_name = "FRWB_Amb"
            case "FLWB_rpm":
                device.units = "rpm"
                device.display_name = "FLWB rpm"
                device.short_name = "FLWB_rpm"
            case "FLWB_ObjTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "FLWB ObjTemp"
                device.short_name = "FLWB_Obj"
            case "FLWB_AmbTemp":
                device.signed = True
                device.units = "°C"
                device.display_name = "FLWB AmbTemp"
                device.short_name = "FLWB_Amb"
            case "IMU_ACCEL_X":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) + (0)
                device.units = "mg"
                device.display_name = "IMU ACCEL X"
                device.short_name = "IMU_ACCE"
            case "IMU_ACCEL_Y":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) + (0)
                device.units = "mg"
                device.display_name = "IMU ACCEL Y"
                device.short_name = "IMU_ACCE"
            case "IMU_ACCEL_Z":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122) + (0)
                device.units = "mg"
                device.display_name = "IMU ACCEL Z"
                device.short_name = "IMU_ACCE"
            case "IMU_GYRO_X":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.5) + (0)
                device.units = "mdps"
                device.display_name = "IMU GYRO X"
                device.short_name = "IMU_GYRO"
            case "IMU_GYRO_Y":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.5) + (0)
                device.units = "mdps"
                device.display_name = "IMU GYRO Y"
                device.short_name = "IMU_GYRO"
            case "IMU_GYRO_Z":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.5) + (0)
                device.units = "mdps"
                device.display_name = "IMU GYRO Z"
                device.short_name = "IMU_GYRO"

            case _:
                pass


def generate_channel_list(devices: List[device_data]) -> List[Tuple[str, str, str, str]]:
    """
    Generate a channel list in the format required by CSV-to-MoTeC conversion.
    Returns: List of (csv_header_name, display_name, short_name, units) tuples
    """
    return [
        (device.name, device.display_name, device.short_name, device.units)
        for device in devices
    ]
