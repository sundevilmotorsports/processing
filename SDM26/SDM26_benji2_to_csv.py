#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from conversion_pipeline import convert_benji2_inputs_to_csv


def parseBenji2File(input_path: str, output_dir: str, session: str):
    csv_output_dir = Path(output_dir) / session
    return convert_benji2_inputs_to_csv(input_path, csv_output_dir, logger=print)


def main():
    parser = argparse.ArgumentParser(description="Convert BENJI2 file(s) to CSV")
    parser.add_argument("input_path", help="Path to a .benji2 file or a folder containing .benji2 files")
    parser.add_argument("output_dir", help="Base output directory for converted CSVs")
    parser.add_argument(
        "--session",
        default=None,
        help="Optional session folder name. Defaults to processed_<input name>",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path)
    default_session = f"processed_{input_path.stem if input_path.is_file() else input_path.name}"
    session = args.session or default_session
    csv_output_dir = Path(args.output_dir) / session

    outputs = convert_benji2_inputs_to_csv(args.input_path, csv_output_dir, logger=print)

    print("\nDONE!")
    print(f"CSV output directory: {csv_output_dir}")
    print(f"Files written: {len(outputs)}")


if __name__ == "__main__":
    main()
