"""
predictive/monitor.py

Simulates real-time sensor monitoring by replaying the IMS
bearing dataset file-by-file. Sends tickets to TriageFlow
API when anomalies are detected.

Usage:
    python -m predictive.monitor \
        --data-dir data/extracted/ims/1st_test/1st_test \
        --equipment-id P-204 \
        --api-url http://localhost:8000
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from predictive.pipeline import TriageFlowPipeline


from datetime import datetime, timezone, timedelta


def replay_sensor_data(
    data_dir: str,
    equipment_id: str,
    api_url: str,
    delay_seconds: float = 0.5,
    models_dir: str = "predictive/saved_models",
    ticket_cooldown_minutes: int = 10,  # ← add this parameter
) -> None:

    pipeline = TriageFlowPipeline(models_dir=models_dir)
    files = sorted(Path(data_dir).glob("*"))
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]

    print(f"Monitoring {equipment_id} — {len(files)} snapshots")
    print(f"API endpoint: {api_url}/tickets/")
    print(f"Ticket cooldown: {ticket_cooldown_minutes} minutes")
    print("-" * 50)

    last_ticket_time = {}  # equipment_id → datetime of last ticket
    last_severity = {}  # equipment_id → last severity level

    SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    for idx, fpath in enumerate(files):
        try:
            raw = pd.read_csv(fpath, sep="\t", header=None).values
        except Exception:
            continue

        signal = raw[:, 0].astype(np.float32)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        result = pipeline.predict(
            signal=signal,
            equipment_id=equipment_id,
            sampling_rate=20480,
        )

        status = "🔴 ANOMALY" if result.is_anomaly else "🟢 Normal"
        print(
            f"[{idx+1:04d}/{len(files)}] {fpath.name} | "
            f"{status} | "
            f"prob={result.anomaly_probability:.4f} | "
            f"fault={result.fault_type} | "
            f"sev={result.severity}"
        )

        if result.is_anomaly:
            now = datetime.now(timezone.utc)
            cooldown = timedelta(minutes=ticket_cooldown_minutes)
            last_time = last_ticket_time.get(equipment_id)
            last_sev = last_severity.get(equipment_id, "low")
            current_rank = SEVERITY_RANK.get(result.severity, 0)
            last_rank = SEVERITY_RANK.get(last_sev, 0)

            # Create ticket if:
            # 1. No previous ticket, OR
            # 2. Cooldown has expired, OR
            # 3. Severity increased (escalation)
            should_create = (
                last_time is None
                or (now - last_time) > cooldown
                or current_rank > last_rank
            )

            if should_create:
                ticket_text = pipeline.generate_ticket_text(result)
                try:
                    resp = requests.post(
                        f"{api_url}/tickets/",
                        json={"raw_text": ticket_text},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        tid = resp.json().get("ticket_id", "N/A")
                        reason = (
                            "first detection"
                            if last_time is None
                            else (
                                "severity escalation"
                                if current_rank > last_rank
                                else "cooldown expired"
                            )
                        )
                        print(f"  → Ticket created: {tid[:8]}... [{reason}]")
                        last_ticket_time[equipment_id] = now
                        last_severity[equipment_id] = result.severity
                    else:
                        print(f"  → API error {resp.status_code}")
                except requests.exceptions.ConnectionError:
                    print(f"  → API not reachable")
            else:
                remaining = int((cooldown - (now - last_time)).total_seconds() / 60)
                print(f"  → Suppressed (cooldown: {remaining}m remaining)")

        time.sleep(delay_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir", required=True, help="Path to IMS snapshot files folder"
    )
    parser.add_argument("--equipment-id", default="P-204")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Seconds between each snapshot"
    )
    parser.add_argument("--models-dir", default="predictive/saved_models")
    args = parser.parse_args()

    replay_sensor_data(
        data_dir=args.data_dir,
        equipment_id=args.equipment_id,
        api_url=args.api_url,
        delay_seconds=args.delay,
        models_dir=args.models_dir,
    )
