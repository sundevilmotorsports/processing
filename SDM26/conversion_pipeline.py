from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Callable

from devices import create_devices, configure_devices, generate_channel_list
from imu_displacement import translate_linear_acc
from motec_ld import MotecChannel, MotecEvent, MotecLog

LogCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int, str], None]


class EmptyBenji2FileError(ValueError):
    """Raised when a BENJI2 file has no readable log payload."""


@dataclass(frozen=True)
class OutputLayout:
    root_dir: Path
    csv_dir: Path
    ld_dir: Path


@dataclass(frozen=True)
class ConversionArtifacts:
    benji_path: Path
    csv_path: Path
    ld_path: Path


def filter_duplicate_headers(header_str: str) -> tuple[str, list[int]]:
    headers = [header.strip() for header in header_str.split(",")]
    base_counts: dict[str, int] = {}
    filtered: list[str] = []

    for header in headers:
        header = header.strip("\x00")
        base = header.rstrip("0123456789").strip()
        if base not in base_counts:
            filtered.append(base)
            base_counts[base] = 1
        else:
            base_counts[base] += 1

    counts = [base_counts[base] for base in filtered]
    return ",".join(filtered), counts


def collect_files(input_path: str | Path, suffix: str) -> list[Path]:
    path = Path(input_path)
    suffix = suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if path.is_file():
        if path.suffix.lower() != suffix:
            raise ValueError(f"Expected a {suffix} file, got: {path.name}")
        return [path]

    if path.is_dir():
        files = sorted(
            (item for item in path.iterdir() if item.is_file() and item.suffix.lower() == suffix),
            key=lambda item: item.name.lower(),
        )
        if not files:
            raise FileNotFoundError(f"No {suffix} files found in {path}")
        return files

    raise ValueError(f"Unsupported input path: {path}")


def build_output_layout(output_dir: str | Path, input_path: str | Path) -> OutputLayout:
    base_output_dir = Path(output_dir)
    source_path = Path(input_path)
    session_name = source_path.stem if source_path.is_file() else source_path.name
    root_dir = base_output_dir / f"converted_{session_name}"
    return OutputLayout(root_dir=root_dir, csv_dir=root_dir / "csv", ld_dir=root_dir / "ld")


def _emit_log(logger: LogCallback | None, message: str) -> None:
    if logger is not None:
        logger(message)


def _emit_progress(progress_callback: ProgressCallback | None, completed: int, total: int, message: str) -> None:
    if progress_callback is not None:
        progress_callback(completed, total, message)


def convert_benji2_file_to_csv(
    benji_path: str | Path,
    csv_path: str | Path,
    logger: LogCallback | None = None,
) -> Path:
    benji_path = Path(benji_path)
    csv_path = Path(csv_path)

    _emit_log(logger, f"BENJI2 -> CSV: {benji_path.name}")

    with open(benji_path, "br") as benji_file:
        header_length_bytes = benji_file.read(4)
        if not header_length_bytes:
            raise EmptyBenji2FileError(f"Skipping empty BENJI2 file: {benji_path.name}")
        if len(header_length_bytes) != 4:
            raise ValueError(f"Missing BENJI2 header length in {benji_path.name}")

        header_length = int.from_bytes(header_length_bytes, "little", signed=False) - 1
        if header_length <= 0:
            raise EmptyBenji2FileError(f"Skipping empty BENJI2 file: {benji_path.name}")

        header_data = benji_file.read(header_length)
        try:
            header = header_data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Unable to decode header in {benji_path.name}: {exc}") from exc

        filtered_header, data_sizes = filter_duplicate_headers(header)
        device_names = [name.strip() for name in filtered_header.split(",")]
        devices = create_devices(device_names, data_sizes)
        configure_devices(devices)

        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="") as csv_file:
            csv_file.write("SAMPLE," + filtered_header + "\n")
            benji_file.read(1)

            sample_number = 0
            written_rows = 0

            while True:
                output_row = [None] * len(devices)
                eof = False

                for device in devices:
                    if device.name == "CH_COUNT":
                        break

                    raw_data = benji_file.read(device.byte_size)
                    if len(raw_data) != device.byte_size:
                        eof = True
                        break

                    output_row[device.column_index] = device.getData(raw_data)

                if eof:
                    break

                sample_number += 1
                output_row.insert(0, sample_number)
                csv_file.write(",".join(str(value) if value is not None else "" for value in output_row) + "\n")
                written_rows += 1

    # translate_linear_acc(str(csv_path))
    _emit_log(logger, f"CSV written: {csv_path} ({written_rows} rows)")
    return csv_path


def convert_benji2_inputs_to_csv(
    input_path: str | Path,
    csv_output_dir: str | Path,
    logger: LogCallback | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    benji_files = collect_files(input_path, ".benji2")
    csv_output_dir = Path(csv_output_dir)
    csv_output_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    total = len(benji_files)

    _emit_progress(progress_callback, 0, total, "Starting BENJI2 -> CSV conversion")

    for index, benji_path in enumerate(benji_files, start=1):
        csv_path = csv_output_dir / f"{benji_path.stem}.csv"
        try:
            convert_benji2_file_to_csv(benji_path, csv_path, logger=logger)
        except EmptyBenji2FileError as exc:
            _emit_log(logger, str(exc))
            _emit_progress(progress_callback, index, total, f"Skipped empty file: {benji_path.name}")
            continue
        outputs.append(csv_path)
        _emit_progress(progress_callback, index, total, f"CSV complete: {benji_path.name}")

    return outputs


def read_csv_file(csv_path: str | Path, max_samples: int | None = None) -> tuple[list[str], list[list[str]]]:
    csv_path = Path(csv_path)
    data: list[list[str]] = []

    with open(csv_path, "r", newline="") as csv_file:
        reader = csv.reader(csv_file)
        try:
            header = next(reader)
        except StopIteration:
            header = []

        for index, row in enumerate(reader):
            if max_samples is not None and index >= max_samples:
                break
            data.append(row)

    return header, data


def is_synthetic_csv_column(header_name: str) -> bool:
    normalized = header_name.strip().lower()
    return not normalized or normalized == "sample" or normalized.startswith("unnamed:")


def infer_sample_rate(
    header: list[str],
    data: list[list[str]],
    default_freq: int = 500,
    max_deltas: int = 1000,
) -> tuple[int, int | None, float | None, float | None]:
    header_map = {column.strip().lower(): index for index, column in enumerate(header)} if header else {}
    time_index = header_map.get("ts")
    if time_index is None:
        return default_freq, None, None, None

    timestamps: list[float] = []
    deltas: list[float] = []
    previous_timestamp: float | None = None

    for row in data:
        try:
            current_timestamp = float(row[time_index])
        except (IndexError, ValueError):
            continue

        timestamps.append(current_timestamp)
        if previous_timestamp is not None:
            delta = current_timestamp - previous_timestamp
            if delta > 0 and len(deltas) < max_deltas:
                deltas.append(delta)
        previous_timestamp = current_timestamp

    if len(timestamps) < 2 or not deltas:
        return default_freq, time_index, None, None

    total_duration = timestamps[-1] - timestamps[0]
    if total_duration <= 0:
        return default_freq, time_index, None, None

    representative_delta = total_duration / (len(timestamps) - 1)
    median_delta = median(deltas)
    inferred_freq = max(1, int(round(1.0 / representative_delta)))
    return inferred_freq, time_index, representative_delta, median_delta


def convert_csv_file_to_motec(
    csv_path: str | Path,
    ld_path: str | Path,
    max_samples: int | None = None,
    logger: LogCallback | None = None,
) -> Path:
    csv_path = Path(csv_path)
    ld_path = Path(ld_path)
    ld_path.parent.mkdir(parents=True, exist_ok=True)

    _emit_log(logger, f"CSV -> LD: {csv_path.name}")

    header, data = read_csv_file(csv_path, max_samples)
    header = [column.strip() for column in header]
    header_map = {column.lower(): index for index, column in enumerate(header)} if header else {}

    device_names = [column for column in header if not is_synthetic_csv_column(column)]
    devices = create_devices(device_names, [4] * len(device_names))
    configure_devices(devices)
    channel_definitions = generate_channel_list(devices)

    freq, _, representative_delta, median_delta = infer_sample_rate(header, data)
    if representative_delta is None:
        _emit_log(logger, f"Using default sample rate: {freq} Hz")
    else:
        _emit_log(
            logger,
            "Sample rate: "
            f"{freq} Hz (average dt {representative_delta:.9f} s, median dt {median_delta:.9f} s)",
        )

    log = MotecLog()
    now = datetime.now()
    log.date = now.strftime("%d/%m/%Y")
    log.time = now.strftime("%H:%M:%S")
    log.driver = "Driver"
    log.vehicle = "Vehicle"
    log.venue = "Track"
    log.comment = "Dynamic Channels from devices.py"
    log.event = MotecEvent(
        {
            "name": "Full Data Session",
            "session": "All Channels from devices.py",
            "comment": f"All {len(channel_definitions)} channels with decplaces=0",
            "venuepos": 0,
        }
    )

    channel_indexes: list[tuple[int, str]] = []
    for index, (csv_name, display_name, short_name, units) in enumerate(channel_definitions):
        channel = MotecChannel(
            {
                "name": display_name,
                "shortname": short_name[:8],
                "units": units,
                "id": 8000 + index,
                "freq": freq,
                "shift": 0,
                "multiplier": 1,
                "scale": 1,
                "decplaces": 0,
                "datatype": 0x07,
                "datasize": 4,
            }
        )
        log.add_channel(channel)

        resolved_index = header_map.get(csv_name.strip().lower())
        if resolved_index is None:
            log.channels.pop()
            log.numchannels = len(log.channels)
            _emit_log(logger, f"Skipping channel missing from CSV header: {csv_name}")
            continue

        channel_indexes.append((resolved_index, csv_name))

    for row in data:
        samples: list[float] = []
        for column_index, _ in channel_indexes:
            try:
                value_str = row[column_index]
                value = 0.0 if value_str in {"", "None"} else float(value_str)
            except (IndexError, ValueError):
                value = 0.0
            samples.append(value)
        log.add_samples(samples)

    ld_path.write_bytes(log.to_string())
    _emit_log(logger, f"LD written: {ld_path} ({len(data)} samples, {len(channel_indexes)} channels)")
    return ld_path


def convert_csv_inputs_to_motec(
    input_path: str | Path,
    ld_output_dir: str | Path,
    max_samples: int | None = None,
    logger: LogCallback | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    csv_files = collect_files(input_path, ".csv")
    ld_output_dir = Path(ld_output_dir)
    ld_output_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    total = len(csv_files)

    _emit_progress(progress_callback, 0, total, "Starting CSV -> LD conversion")

    for index, csv_path in enumerate(csv_files, start=1):
        ld_path = ld_output_dir / f"{csv_path.stem}.ld"
        convert_csv_file_to_motec(csv_path, ld_path, max_samples=max_samples, logger=logger)
        outputs.append(ld_path)
        _emit_progress(progress_callback, index, total, f"LD complete: {csv_path.name}")

    return outputs


def convert_benji2_inputs_to_outputs(
    input_path: str | Path,
    output_dir: str | Path,
    max_samples: int | None = None,
    logger: LogCallback | None = None,
    progress_callback: ProgressCallback | None = None,
) -> tuple[OutputLayout, list[ConversionArtifacts]]:
    benji_files = collect_files(input_path, ".benji2")
    layout = build_output_layout(output_dir, input_path)
    layout.csv_dir.mkdir(parents=True, exist_ok=True)
    layout.ld_dir.mkdir(parents=True, exist_ok=True)

    total_steps = len(benji_files) * 2
    completed_steps = 0
    results: list[ConversionArtifacts] = []

    _emit_log(logger, f"Output root: {layout.root_dir}")
    _emit_log(logger, f"CSV output: {layout.csv_dir}")
    _emit_log(logger, f"LD output: {layout.ld_dir}")
    _emit_progress(progress_callback, completed_steps, total_steps, "Ready")

    for index, benji_path in enumerate(benji_files, start=1):
        _emit_log(logger, f"[{index}/{len(benji_files)}] Processing {benji_path.name}")

        csv_path = layout.csv_dir / f"{benji_path.stem}.csv"
        try:
            convert_benji2_file_to_csv(benji_path, csv_path, logger=logger)
        except EmptyBenji2FileError as exc:
            _emit_log(logger, str(exc))
            completed_steps += 2
            _emit_progress(progress_callback, completed_steps, total_steps, f"Skipped empty file: {benji_path.name}")
            continue
        completed_steps += 1
        _emit_progress(progress_callback, completed_steps, total_steps, f"CSV complete: {benji_path.name}")

        ld_path = layout.ld_dir / f"{benji_path.stem}.ld"
        convert_csv_file_to_motec(csv_path, ld_path, max_samples=max_samples, logger=logger)
        completed_steps += 1
        _emit_progress(progress_callback, completed_steps, total_steps, f"LD complete: {benji_path.name}")

        results.append(ConversionArtifacts(benji_path=benji_path, csv_path=csv_path, ld_path=ld_path))

    return layout, results


__all__ = [
    "ConversionArtifacts",
    "EmptyBenji2FileError",
    "OutputLayout",
    "build_output_layout",
    "collect_files",
    "convert_benji2_file_to_csv",
    "convert_benji2_inputs_to_csv",
    "convert_benji2_inputs_to_outputs",
    "convert_csv_file_to_motec",
    "convert_csv_inputs_to_motec",
    "filter_duplicate_headers",
    "infer_sample_rate",
    "is_synthetic_csv_column",
    "read_csv_file",
]
