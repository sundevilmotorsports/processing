#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime
import struct

# Import MoTeC format classes from local file
try:
    from SDM26.motec_ld import MotecLog, MotecChannel, MotecEvent
except ImportError:
    print("ERROR: motec_ld.py not found!")
    exit(1)

# -----------------------------
# CONFIG: ALL CHANNELS
# -----------------------------
ALL_CHANNELS = [
    # (name, units)
    ("Time", "s"),
    ("F_BRAKEPRESSURE", "kPa"),
    ("R_BRAKEPRESSURE", "kPa"),
    ("STEERING", "deg"),
    ("FLSHOCK", "mm"),
    ("FRSHOCK", "mm"),
    ("RRSHOCK", "mm"),
    ("RLSHOCK", "mm"),
    ("CURRENT", "A"),
    ("BATTERY", "V"),
    ("IMU_X_ACCEL", "g"),
    ("IMU_Y_ACCEL", "g"),
    ("IMU_Z_ACCEL", "g"),
    ("IMU_X_GYRO", "deg/s"),
    ("IMU_Y_GYRO", "deg/s"),
    ("IMU_Z_GYRO", "deg/s"),
    ("FR_SG", "raw"),
    ("FL_SG", "raw"),
    ("RL_SG", "raw"),
    ("RR_SG", "raw"),
]

# -----------------------------
# HELPER: Parse BENJI2 (fake data for now)
# -----------------------------
def parse_benji2_fake(file_path, max_samples=None):
    print(f"[DEBUG] Parsing BENJI2 file (FAKE TS): {file_path}")
    n_samples = 1000 if max_samples is None else max_samples
    n_channels = len(ALL_CHANNELS)
    samples = []

    freq = 500  # Hz
    for i in range(n_samples):
        row = []
        # Fake TS (monotonic)
        row.append(i / freq)
        # Fake other channel data (just i*value for visibility)
        for c in range(1, n_channels):
            row.append((i * (c + 1)) % 1000)
        samples.append(row)

    print(f"[DEBUG] Parsed {len(samples)} samples, {len(samples[0])} channels")
    print("[DEBUG] First 5 samples:")
    for s in samples[:5]:
        print("  ", s)
    return samples, freq

# -----------------------------
# Convert to MoTeC
# -----------------------------
def convert_to_motec(samples, freq, output_path):
    print(f"[DEBUG] Converting to MoTeC: {output_path}")
    log = MotecLog()
    now = datetime.now()
    log.date = now.strftime('%d/%m/%Y')
    log.time = now.strftime('%H:%M:%S')
    log.driver = "Driver"
    log.vehicle = "Vehicle"
    log.venue = "Track"
    log.comment = "BENJI2 -> MoTeC (Fake TS for debug)"

    log.event = MotecEvent({
        "name": "Debug Session",
        "session": "All Channels Fixed",
        "comment": f"{len(ALL_CHANNELS)} channels",
        "venuepos": 0
    })

    # Add channels
    ch_objects = []
    for i, (name, units) in enumerate(ALL_CHANNELS):
        ch_def = {
            "name": name,
            "shortname": name[:8],
            "units": units,
            "id": 8000 + i,
            "freq": freq,
            "shift": 0,
            "multiplier": 1,
            "scale": 1,
            "decplaces": 2,
            "datatype": 0x07,
            "datasize": 4
        }
        ch = MotecChannel(ch_def)
        log.add_channel(ch)
        ch_objects.append(ch)
        if i < 5 or i % 5 == 0:
            print(f"[DEBUG] Added channel: {name} (ID {ch.id})")

    # Set time channel correctly
    for ch in log.channels:
        if ch.name == "Time":
            log.time_channel = ch
            print(f"[DEBUG] Time channel set: {ch.name} (ID {ch.id})")
            break

    # Add samples
    print("[DEBUG] Adding samples...")
    for row_idx, row in enumerate(samples):
        log.add_samples(row)
        if row_idx < 5:
            print(f"[DEBUG] Sample {row_idx}: {row}")

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(log.to_string())
    print(f"[DEBUG] MoTeC file written: {output_path} ({len(samples)} samples, {len(samples[0])} channels)")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python process_benji2_motec_debug.py <benji2_file> [output.ld]")
        exit(1)

    benji2_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "output/debug.ld"

    samples, freq = parse_benji2_fake(benji2_file)
    convert_to_motec(samples, freq, output_file)
