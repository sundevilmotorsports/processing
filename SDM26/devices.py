from typing import List, Tuple, Callable

class device_data:
    name: str
    column_index: int
    byte_size: int
    conversion_factor: Callable | float = 1.0
    signed: bool = False
    byte_order: str = "little"

    def __init__(self, name: str, column_index: int, byte_size: int,
                 conversion_factor: Callable | float = 1.0,
                 signed: bool = False,
                 byte_order: str = "little"):
        self.name = name
        self.column_index = column_index
        self.byte_size = byte_size
        self.conversion_factor = conversion_factor
        self.signed = signed
        self.byte_order = byte_order

    def getData(self, data: bytes):
        value = int.from_bytes(data, byteorder=self.byte_order, signed=self.signed)
        if callable(self.conversion_factor):
            return self.conversion_factor(value)
        return value * self.conversion_factor


def create_devices(device_names: List[str], data_sizes: List[int]) -> List[device_data]:
    return [device_data(name.strip(), i, data_sizes[i]) for i, name in enumerate(device_names)]


def configure_devices(devices: List[device_data]) -> None:
    """
    Apply per-device conversion_factor and signed flags in a single place.
    Call this after creating devices so all files share the same rules.
    """
    for device in devices:
        name = device.name
        # Keep these rules in sync with your other files
        match name:
            case "TS":
                device.conversion_factor = 1e-6
            case "CURRENT":
                device.conversion_factor = 1.25
                device.signed = True
            case "BATTERY":
                device.conversion_factor = 1.25 / 1000
                device.signed = True
            case "FL_SG":
                device.conversion_factor = lambda v: (-11052026.1 * v + 2606.22253)
            case "FR_SG":
                device.conversion_factor = lambda v: (v)
            case "RL_SG":
                device.conversion_factor = lambda v: (-1401922.44 * v + 92026.0137)
            case "RR_SG":
                device.conversion_factor = lambda v: (v)
            case "IMU_X_ACCEL" | "IMU_Y_ACCEL" | "IMU_Z_ACCEL":
                device.signed = True
                device.conversion_factor = lambda v: (v * 0.122)
            case "IMU_X_GYRO" | "IMU_Y_GYRO" | "IMU_Z_GYRO":
                device.signed = True
                device.conversion_factor = lambda v: (v * 17.50)
            case "FLW_AMB" | "FRW_AMB" | "RLW_AMB" | "RRW_AMB" | \
                 "FLW_OBJ" | "FRW_OBJ" | "RLW_OBJ" | "RRW_OBJ":
                device.conversion_factor = lambda v: ((v * 0.02) - 273.15)
            case "STEERING":
                device.conversion_factor = lambda v: ((0.084769) * (v) + (-152.846451))
            case "FRSHOCK":
                device.conversion_factor = lambda v: ((-0.018444) * (v) + (75.894221))
            case "FLSHOCK":
                device.conversion_factor = lambda v: ((-0.018586) * (v) + (76.399026))
            case "RLSHOCK":
                device.conversion_factor = lambda v: ((-0.018600) * (v) + (76.618397))
            case "RRSHOCK":
                device.conversion_factor = lambda v: ((-0.018498) * (v) + (76.591013))
            case _:
                pass