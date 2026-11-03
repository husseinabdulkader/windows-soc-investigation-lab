"""Small offline detector for the explicitly documented lab CSV schema."""

import argparse
import csv
from datetime import datetime, timedelta
import ipaddress
import json
from pathlib import Path
import sys


FIELDS = ["synthetic", "record_id", "timestamp", "event_id", "computer",
          "target_domain", "target_user", "source_ip", "logon_type"]
IDENTITY = ("computer", "target_domain", "target_user", "source_ip", "logon_type")
WINDOW = timedelta(minutes=5)
THRESHOLD = 5


def load_events(path):
    """Validate all rows before analysis; never silently drop malformed evidence."""
    events, seen = [], set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV header must exactly match docs/schema.md")
        for line, row in enumerate(reader, start=2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("wrong column count")
                if any(v != v.strip() for v in row.values()):
                    raise ValueError("leading/trailing whitespace is not allowed")
                if row["synthetic"] != "true":
                    raise ValueError("v1 accepts only explicitly synthetic data")
                if not row["record_id"] or row["record_id"] in seen:
                    raise ValueError("record_id must be nonempty and globally unique")
                if not row["timestamp"].endswith("Z"):
                    raise ValueError("timestamp must use UTC Z suffix")
                stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                if row["event_id"] not in ("4624", "4625"):
                    raise ValueError("event_id must be 4624 or 4625")
                if row["logon_type"] not in ("2", "3", "4", "5", "7", "8", "9", "10", "11", "12", "13"):
                    raise ValueError("unsupported logon_type")
                for field in ("computer", "target_domain", "target_user"):
                    if not row[field] or row[field] == "-":
                        raise ValueError(f"{field} is required")
                if row["source_ip"] != "-":
                    address = ipaddress.ip_address(row["source_ip"])
                    if str(address) != row["source_ip"]:
                        raise ValueError("source_ip must be canonical IP text")
                seen.add(row["record_id"])
                events.append({**row, "time": stamp})
            except ValueError as exc:
                raise ValueError(f"line {line}: {exc}") from exc
    if not events:
        raise ValueError("CSV contains no events")
    return sorted(events, key=lambda e: (e["time"], e["event_id"] == "4624", e["record_id"]))


def key(event):
    return tuple(event[field].casefold() for field in IDENTITY)


def detect(events):
    """One alert per success; use failures since the previous matching success."""
    pending, alerts = {}, []
    for event in sorted(events, key=lambda e: (e["time"], e["event_id"] == "4624", e["record_id"])):
        # This first rule is deliberately restricted to attributable network logons.
        if event["logon_type"] != "3" or event["source_ip"] == "-":
            continue
        group = pending.setdefault(key(event), [])
        # No useful failure can be more than two five-minute windows old.
        group[:] = [f for f in group if event["time"] - f["time"] <= 2 * WINDOW]
        if event["event_id"] == "4625":
            group.append(event)
            continue
        before = [f for f in group if f["time"] < event["time"]]
        if before:
            last = before[-1]
            burst = [f for f in before if last["time"] - f["time"] <= WINDOW]
            if len(burst) >= THRESHOLD and event["time"] - last["time"] <= WINDOW:
                alerts.append({
                    "rule": "AUTH-001", "synthetic": True,
                    "success_record_id": event["record_id"],
                    "success_time": event["timestamp"],
                    "computer": event["computer"],
                    "account": event["target_domain"] + "\\" + event["target_user"],
                    "source_ip": event["source_ip"], "logon_type": 3,
                    "failure_count": len(burst),
                    "first_failure_time": burst[0]["timestamp"],
                    "last_failure_time": last["timestamp"],
                    "failure_record_ids": [f["record_id"] for f in burst],
                })
        # Timestamp ties have no reliable causal order. Discard tied failures too.
        pending[key(event)] = [f for f in group if f["time"] > event["time"]]
    return alerts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        events = load_events(args.csv_path)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.validate_only:
        print(f"Validated {len(events)} synthetic events.")
    else:
        print(json.dumps({"event_count": len(events), "alerts": detect(events)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
