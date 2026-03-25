#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from conversion_pipeline import convert_csv_file_to_motec, convert_csv_inputs_to_motec


def convert_csv_to_motec_fixed(csv_path, output_filename, max_samples=None):
    output_dir = Path(__file__).resolve().parent / "output"
    ld_path = output_dir / output_filename
    return convert_csv_file_to_motec(csv_path, ld_path, max_samples=max_samples, logger=print)


def main():
    parser = argparse.ArgumentParser(description="Convert CSV file(s) to MoTeC LD format")
    parser.add_argument("input_path", help="Path to a CSV file or a folder containing CSV files")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "output"),
        help="Directory for generated .ld files",
    )
    parser.add_argument(
        "--samples",
        "-s",
        type=int,
        default=None,
        help="Max samples to convert per file (default: all)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    outputs = convert_csv_inputs_to_motec(
        args.input_path,
        output_dir,
        max_samples=args.samples,
        logger=print,
    )

    print("\nDONE!")
    print(f"LD output directory: {output_dir}")
    print(f"Files written: {len(outputs)}")


if __name__ == "__main__":
    main()
