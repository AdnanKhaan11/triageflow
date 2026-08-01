"""
predictive/generate_synthetic_data.py

Generates synthetic bearing vibration data that mimics the IMS dataset
structure exactly — same file naming, same format, same signal patterns.

Three phases simulated:
  1. Healthy (first 30% of files)  — low amplitude, smooth vibration
  2. Degrading (middle 40%)        — gradually increasing amplitude
  3. Faulty (last 30%)             — high kurtosis, impulsive spikes

Usage:
    python -m predictive.generate_synthetic_data
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


def generate_healthy_signal(
    n_samples: int = 20480,
    sampling_rate: int = 20480,
) -> np.ndarray:
    """
    Healthy bearing: low-amplitude broadband vibration
    with a dominant shaft frequency component.
    """
    t = np.linspace(0, n_samples / sampling_rate, n_samples)

    # Shaft rotation frequency and harmonics
    shaft_freq = 33.3  # Hz (2000 RPM)
    signal = (
        0.05 * np.sin(2 * np.pi * shaft_freq * t)
        + 0.02 * np.sin(2 * np.pi * shaft_freq * 2 * t)
        + 0.01 * np.sin(2 * np.pi * shaft_freq * 3 * t)
    )

    # Background noise
    signal += np.random.normal(0, 0.03, n_samples)
    return signal.astype(np.float32)


def generate_degrading_signal(
    n_samples: int = 20480,
    sampling_rate: int = 20480,
    severity: float = 0.5,  # 0.0 = early, 1.0 = near failure
) -> np.ndarray:
    """
    Degrading bearing: increasing amplitude and kurtosis.
    severity controls how far into degradation (0 to 1).
    """
    t = np.linspace(0, n_samples / sampling_rate, n_samples)

    shaft_freq = 33.3
    bearing_freq = 120.0  # Ball Pass Frequency Outer race (BPFO)

    # Shaft harmonics
    signal = 0.05 * np.sin(2 * np.pi * shaft_freq * t) + 0.02 * np.sin(
        2 * np.pi * shaft_freq * 2 * t
    )

    # Growing bearing fault frequency
    fault_amp = 0.05 + severity * 0.15
    signal += fault_amp * np.sin(2 * np.pi * bearing_freq * t)

    # Occasional impacts (growing with severity)
    impact_rate = int(sampling_rate / (bearing_freq * (1 + severity)))
    for i in range(0, n_samples, impact_rate):
        width = np.random.randint(5, 15)
        amp = (0.05 + severity * 0.2) * np.random.uniform(0.8, 1.2)
        end = min(i + width, n_samples)
        signal[i:end] += amp * np.random.randn(end - i)

    # Background noise
    signal += np.random.normal(0, 0.04 + severity * 0.03, n_samples)
    return signal.astype(np.float32)


def generate_faulty_signal(
    n_samples: int = 20480,
    sampling_rate: int = 20480,
) -> np.ndarray:
    """
    Faulty bearing: high kurtosis, strong impulsive pattern,
    elevated RMS, clearly distinguishable from healthy.
    """
    t = np.linspace(0, n_samples / sampling_rate, n_samples)

    shaft_freq = 33.3
    bearing_freq = 120.0

    # Shaft harmonics (still present)
    signal = 0.05 * np.sin(2 * np.pi * shaft_freq * t) + 0.03 * np.sin(
        2 * np.pi * shaft_freq * 2 * t
    )

    # Strong bearing fault frequency
    signal += 0.25 * np.sin(2 * np.pi * bearing_freq * t)
    signal += 0.10 * np.sin(2 * np.pi * bearing_freq * 2 * t)

    # Dense impulsive spikes — hallmark of bearing failure
    impact_interval = int(sampling_rate / bearing_freq)
    for i in range(0, n_samples, impact_interval):
        # Main impact
        width = np.random.randint(8, 20)
        amp = np.random.uniform(0.4, 0.8)
        end = min(i + width, n_samples)
        signal[i:end] += (
            amp * np.exp(-np.linspace(0, 5, end - i)) * np.random.choice([-1, 1])
        )

        # Secondary resonance ring-down
        if i + 50 < n_samples:
            ring_len = min(50, n_samples - i)
            signal[i : i + ring_len] += (
                0.15
                * np.sin(2 * np.pi * 2000 * t[i : i + ring_len])
                * np.exp(-np.linspace(0, 3, ring_len))
            )

    # Elevated background noise
    signal += np.random.normal(0, 0.06, n_samples)
    return signal.astype(np.float32)


def generate_synthetic_ims_dataset(
    output_dir: str = "data/extracted/ims/1st_test/1st_test",
    n_files: int = 150,
    n_samples: int = 20480,
    n_channels: int = 4,
    seed: int = 42,
) -> None:
    """
    Creates a directory of synthetic IMS-format snapshot files.

    File structure mirrors the real IMS dataset exactly:
    - Tab-separated values, no header
    - One row per sample, one column per bearing channel
    - Filenames are timestamps (matching IMS naming convention)
    - Files are sorted chronologically (alphabetical = temporal)

    Phase distribution:
    - Files 0-44   (30%): Healthy bearings
    - Files 45-99  (37%): Gradually degrading
    - Files 100-149 (33%): Clear bearing faults

    Args:
        output_dir:  Where to write the files
        n_files:     Total number of snapshot files to generate
        n_samples:   Samples per file per channel (IMS uses 20480)
        n_channels:  Number of bearing channels (IMS uses 4)
        seed:        Random seed for reproducibility
    """
    np.random.seed(seed)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Phase boundaries
    healthy_end = int(n_files * 0.30)
    faulty_start = int(n_files * 0.67)

    # Generate timestamps matching IMS naming: YYYY.MM.DD.HH.MM.SS
    # Start from a realistic date, spaced 10 minutes apart
    start_dt = datetime(2003, 10, 22, 12, 6, 24)
    interval = timedelta(minutes=10)

    print(f"Generating {n_files} synthetic IMS snapshot files...")
    print(f"  Output: {out_path.resolve()}")
    print(f"  Healthy:   files 0-{healthy_end-1}")
    print(f"  Degrading: files {healthy_end}-{faulty_start-1}")
    print(f"  Faulty:    files {faulty_start}-{n_files-1}")
    print(f"  Format:    {n_samples} samples × {n_channels} channels")
    print()

    for file_idx in range(n_files):
        ts = start_dt + interval * file_idx
        filename = ts.strftime("%Y.%m.%d.%H.%M.%S")
        fpath = out_path / filename

        # Determine phase and severity
        if file_idx < healthy_end:
            phase = "healthy"
            channels = [generate_healthy_signal(n_samples) for _ in range(n_channels)]

        elif file_idx < faulty_start:
            phase = "degrading"
            # Severity increases linearly through degrading phase
            severity = (file_idx - healthy_end) / (faulty_start - healthy_end)
            channels = [
                generate_degrading_signal(n_samples, severity=severity)
                for _ in range(n_channels)
            ]

        else:
            phase = "faulty"
            channels = [generate_faulty_signal(n_samples) for _ in range(n_channels)]

        # Stack channels as columns: shape (n_samples, n_channels)
        data = np.column_stack(channels)
        df = pd.DataFrame(data)

        # Write tab-separated, no header, 6 decimal places
        df.to_csv(fpath, sep="\t", header=False, index=False, float_format="%.6f")

        if file_idx % 30 == 0 or file_idx == n_files - 1:
            rms = float(np.sqrt(np.mean(channels[0] ** 2)))
            print(
                f"  [{file_idx+1:3d}/{n_files}] "
                f"{filename} | "
                f"phase={phase:10s} | "
                f"RMS={rms:.4f}"
            )

    print(f"\nDone. {n_files} files written to {out_path.resolve()}")
    print("\nTo run the monitor:")
    print(f"  python -m predictive.monitor \\")
    print(f"    --data-dir {output_dir} \\")
    print(f"    --equipment-id P-204 \\")
    print(f"    --api-url http://localhost:8000 \\")
    print(f"    --delay 0.3")


if __name__ == "__main__":
    generate_synthetic_ims_dataset(
        output_dir="data/extracted/ims/1st_test/1st_test",
        n_files=150,
        n_samples=20480,
        n_channels=4,
        seed=42,
    )
