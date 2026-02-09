"""
Read scalar results from a single experiment directory.
Supports: (1) CSV export from opp_scavetool, (2) legacy text .sca, (3) SQLite .sca.
Returns a list of dicts { module, name, value } for each scalar.
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


SCALAR_NAMES = [
    "Generated", "TX_Attempts", "Delivered", "Collisions", "RetriesExhausted",
    "PDR", "E2EDelayMean", "E2EDelayMax", "E2EDelayJitter",
    "DeadlineMisses", "DeadlineMissRatio", "AvgTxAttemptsPerDelivery",
]


def read_scalars_from_dir(run_dir: Path) -> list[dict]:
    """Load all scalar records from a run directory. Returns list of { module, name, value }."""
    run_dir = Path(run_dir)
    # 1) Prefer CSV (scavetool export)
    for p in run_dir.glob("*.csv"):
        rows = _read_scalars_csv(p)
        if rows:
            return rows
    # 2) Try .sca as text then SQLite
    for p in run_dir.glob("*.sca"):
        rows = _read_sca(p)
        if rows:
            return rows
    return []


def _read_scalars_csv(path: Path) -> list[dict]:
    """Parse CSV with columns run, type, module, name, value (scavetool style)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            return []
        fieldnames = [x.strip() for x in (r.fieldnames or [])]
        need = {"module", "name", "value"}
        if not need.issubset(set(fieldnames)):
            # Alternative: module, name, value only
            if "module" in fieldnames and "name" in fieldnames and "value" in fieldnames:
                pass
            else:
                return []
        for line in r:
            if line.get("type") == "scalar" or "type" not in line:
                try:
                    val = line.get("value", "")
                    if val == "" or val is None:
                        continue
                    value = float(val)
                except (TypeError, ValueError):
                    continue
                module = line.get("module", "")
                name = line.get("name", "")
                if name in SCALAR_NAMES or not SCALAR_NAMES:
                    rows.append({"module": module, "name": name, "value": value})
    return rows


def _read_sca(path: Path) -> list[dict]:
    """Read .sca: try SQLite first, then legacy text format."""
    with open(path, "rb") as f:
        head = f.read(16)
    if head.startswith(b"SQLite"):
        return _read_sca_sqlite(path)
    return _read_sca_text(path)


def _read_sca_sqlite(path: Path) -> list[dict]:
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        # Common OMNeT++ scalar table
        try:
            cur.execute("SELECT module, name, value FROM scalar")
        except sqlite3.OperationalError:
            try:
                cur.execute("SELECT module, name, value FROM scalars")
            except sqlite3.OperationalError:
                conn.close()
                return []
        rows = []
        for row in cur.fetchall():
            module, name, val = row[0], row[1], row[2]
            if name not in SCALAR_NAMES:
                continue
            try:
                value = float(val)
            except (TypeError, ValueError):
                continue
            rows.append({"module": module, "name": name, "value": value})
        conn.close()
        return rows
    except Exception:
        return []


def _read_sca_text(path: Path) -> list[dict]:
    """Legacy text .sca: lines like 'scalar\trunId\tmodule\tname\tvalue' or similar."""
    rows = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 5:
                    continue
                if parts[0].lower() != "scalar":
                    continue
                # scalar runId module name value
                module, name, value_str = parts[2], parts[3], parts[4]
                if name not in SCALAR_NAMES:
                    continue
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                rows.append({"module": module, "name": name, "value": value})
    except Exception:
        pass
    return rows
