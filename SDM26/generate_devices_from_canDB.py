import cantools
from pathlib import Path

def make_short_name(name: str, seen_names: set) -> str:
    """
    100% Dynamic abbreviation that prevents MoTeC collisions.
    It structurally prioritizes names like 'IMU_X' and automatically 
    falls back to 'GYRO_X' if 'IMU_X' is already taken.
    """
    if len(name) <= 8 and name not in seen_names:
        seen_names.add(name)
        return name
    
    parts = name.split('_')
    candidates = []
    
    # Identify "designators" (like X, Y, Z, FL, RR)
    designators = [p for p in parts if len(p) <= 2]
    desig = designators[-1] if designators else None
    
    # Identify descriptive words
    long_parts = [p for p in parts if len(p) > 2]
    
    if desig:
        if long_parts:
            # Candidate 1: 1st word + designator (e.g., IMU_X)
            candidates.append(f"{long_parts[0][:5]}_{desig}")
            if len(long_parts) > 1:
                # Candidate 2: 2nd word + designator (e.g., ACCEL_X or GYRO_X)
                candidates.append(f"{long_parts[1][:5]}_{desig}")
    
    # Candidate 3: Standard prefix/suffix (e.g., ENGI_Oil)
    if len(parts) >= 2:
        candidates.append(f"{parts[0][:4]}_{parts[-1][:3]}")
        
    # Candidate 4: First 4 + Last 4
    candidates.append(name[:4] + name[-4:])
    # Candidate 5: Just truncate
    candidates.append(name[:8])
    
    # Return the first candidate that hasn't been used yet!
    for cand in candidates:
        if len(cand) <= 8 and cand not in seen_names:
            seen_names.add(cand)
            return cand
            
    # Ultimate fallback if everything collides (just append a number)
    for i in range(1, 99):
        cand = f"{name[:6]}{i:02d}"
        if cand not in seen_names:
            seen_names.add(cand)
            return cand

    return name[:8]


def generate_devices_py(dbc_filename="SDM26.dbc", output_filename="devices.py"):
    script_dir = Path(__file__).resolve().parent
    dbc_path = script_dir / dbc_filename
    output_path = script_dir / output_filename

    if not dbc_path.exists():
        print(f"❌ ERROR: Cannot find DBC at {dbc_path}")
        return

    print(f"Loading DBC: {dbc_path.name}...")
    db = cantools.database.load_file(str(dbc_path))

    # Keep track of short names so we NEVER generate a duplicate
    used_short_names = set(["Time"])

    case_blocks = [
        '            case "TS":\n'
        '                device.conversion_factor = 1e-6\n'
        '                device.units = "s"\n'
        '                device.display_name = "Time"\n'
        '                device.short_name = "Time"\n'
    ]
    
    for msg in db.messages:
        for sig in msg.signals:
            scale = sig.scale if sig.scale is not None else 1.0
            offset = sig.offset if sig.offset is not None else 0.0
            is_signed = sig.is_signed
            raw_unit = sig.unit if sig.unit else "raw"

            # --- Unit Conversion Logic ---
            is_milli = raw_unit.startswith('m') and len(raw_unit) > 1 and raw_unit not in ["m", "mm"]
            
            if is_milli:
                if raw_unit == "mg": clean_unit = "G"
                elif raw_unit == "mdps": clean_unit = "deg/s" # Optional: MoTeC prefers deg/s
                else: clean_unit = raw_unit[1:]
            else:
                clean_unit = raw_unit

            display_name = sig.name.replace("_", " ")
            short_name = make_short_name(sig.name, used_short_names)

            block = f'            case "{sig.name}":\n'
            
            if is_signed:
                block += f'                device.signed = True\n'
                
            # --- Dynamic Lambda Formatting (No messy + 0.0) ---
            if is_milli:
                if offset == 0.0:
                    block += f'                device.conversion_factor = lambda v: (v * {scale}) / 1000\n'
                else:
                    block += f'                device.conversion_factor = lambda v: ((v * {scale}) + ({offset})) / 1000\n'
            elif scale != 1.0 or offset != 0.0:
                if offset == 0.0:
                    block += f'                device.conversion_factor = lambda v: (v * {scale})\n'
                else:
                    block += f'                device.conversion_factor = lambda v: (v * {scale}) + ({offset})\n'
            
            block += f'                device.units = "{clean_unit}"\n'
            block += f'                device.display_name = "{display_name}"\n'
            block += f'                device.short_name = "{short_name}"\n'
                
            case_blocks.append(block)

    all_cases_str = "".join(case_blocks)

    template = f"""from typing import List, Tuple, Callable

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
    \"\"\"
    Apply per-device conversion_factor, signed flags, units, and display names.
    \"\"\"
    for device in devices:
        match device.name:
{all_cases_str}
            case _:
                pass


def generate_channel_list(devices: List[device_data]) -> List[Tuple[str, str, str, str]]:
    \"\"\"
    Generate a channel list in the format required by CSV-to-MoTeC conversion.
    Returns: List of (csv_header_name, display_name, short_name, units) tuples
    \"\"\"
    return [
        (device.name, device.display_name, device.short_name, device.units)
        for device in devices
    ]
"""

    with open(output_path, "w") as f:
        f.write(template)

    print(f"✅ Successfully generated '{output_path.name}' from '{dbc_filename}'!")

if __name__ == "__main__":
    generate_devices_py("canDBs/SDM26.dbc", "devices_generated.py")