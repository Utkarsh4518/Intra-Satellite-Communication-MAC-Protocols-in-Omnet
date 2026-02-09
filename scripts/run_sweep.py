#!/usr/bin/env python3
"""
Automated experiment sweep for LiFi hidden-node simulation.

Sweeps: node count, offered load (packetInterval), MAC protocol.
Runs batch simulations with unique experiment IDs and organized output directories.
No result analysis; only execution and directory organization.

Usage:
  From project root: python scripts/run_sweep.py [sweep_config.yaml]
  Default config: scripts/sweep_config.yaml (fallback: scripts/sweep_config_example.yaml)
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path


# Default paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INI = PROJECT_ROOT / "simulations" / "omnetpp.ini"
DEFAULT_RESULTS_ROOT = PROJECT_ROOT / "results" / "sweep"
# Executable: src/LiFiHiddenNode2 or src/LiFiHiddenNode2.exe
def _default_exe():
    p = PROJECT_ROOT / "src" / "LiFiHiddenNode2"
    if not p.suffix and sys.platform == "win32":
        exe = PROJECT_ROOT / "src" / "LiFiHiddenNode2.exe"
        if exe.exists():
            return exe
    return p


def load_config(path: Path) -> dict:
    """Load YAML config. If PyYAML missing, use a minimal built-in parser for our keys."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        # Minimal YAML-like parsing for the keys we need
        out = {}
        current = None
        for line in text.splitlines():
            line = line.split("#")[0].rstrip()
            if not line:
                continue
            if line.endswith(":"):
                current = line[:-1].strip()
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip()
                if k == "base_seed":
                    out["base_seed"] = int(v)
                elif k == "sim_time_limit":
                    out["sim_time_limit"] = int(v)
                elif k == "network":
                    out["network"] = v.strip('"')
                elif k == "node_counts":
                    out["node_counts"] = _parse_list_int(v)
                elif k == "offered_loads":
                    out["offered_loads"] = _parse_list_float(v)
                elif k == "mac_protocols":
                    out["mac_protocols"] = _parse_list(v)
                elif k == "sim_exe" and v:
                    out["sim_exe"] = v.strip('"')
                elif k == "ini_file" and v:
                    out["ini_file"] = v.strip('"')
                elif k == "results_root" and v:
                    out["results_root"] = v.strip('"')
        return out


def _parse_list(s: str) -> list[str]:
    s = s.strip()
    if s.startswith("["):
        s = s[1:].rstrip("]")
    return [x.strip() for x in s.split(",") if x.strip()]


def _parse_list_float(s: str) -> list[float]:
    return [float(x.strip()) for x in _parse_list(s)]


def _parse_list_int(s: str) -> list[int]:
    return [int(x.strip()) for x in _parse_list(s)]


def num_nodes_ini_key(network: str) -> str:
    """e.g. lifihiddennode.LiFiHiddenRing -> lifihiddennode.LiFiHiddenRing.numNodes"""
    return f"{network}.numNodes"


def run_one(
    exe: Path,
    ini: Path,
    out_dir: Path,
    network: str,
    num_nodes: int,
    mac: str,
    packet_interval: float,
    sim_time_limit: int,
    seed: int,
    neds: str,
) -> bool:
    """Run a single experiment. Returns True on success."""
    num_key = num_nodes_ini_key(network)
    # Output directory: OMNeT++ may use **.result-dir; if not supported, run with cwd=out_dir so outputs land there
    out_dir_str = str(out_dir.resolve())
    args = [
        str(exe),
        "-u", "Cmdenv",
        "-n", neds,
        "-f", str(ini.resolve()),
        f"--**.result-dir={out_dir_str}",
        "--network", network,
        f"--{num_key}={num_nodes}",
        "--**.macType", mac,
        "--**.mac.packetInterval", str(packet_interval),
        "--sim-time-limit", f"{sim_time_limit}s",
        "--seed-set", str(seed),
    ]
    try:
        # Run from project root so -n and -f paths resolve; result-dir sends outputs to out_dir
        subprocess.run(args, cwd=str(PROJECT_ROOT), check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print(f"Error: executable not found: {exe}", file=sys.stderr)
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Run automated experiment sweeps (no analysis).")
    ap.add_argument("config", nargs="?", default=None, help="Path to sweep config YAML")
    ap.add_argument("--dry-run", action="store_true", help="Print runs and manifest only, do not execute")
    args = ap.parse_args()

    config_path = args.config
    if not config_path:
        for name in ("sweep_config.yaml", "sweep_config_example.yaml"):
            p = PROJECT_ROOT / "scripts" / name
            if p.exists():
                config_path = str(p)
                break
    if not config_path or not os.path.isfile(config_path):
        print("No sweep_config.yaml or sweep_config_example.yaml found. Pass config path.", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(Path(config_path))
    base_seed = int(cfg.get("base_seed", 1000))
    sim_time_limit = int(cfg.get("sim_time_limit", 50))
    network = cfg.get("network", "lifihiddennode.LiFiHiddenRing")
    node_counts = cfg.get("node_counts", [4, 8])
    offered_loads = cfg.get("offered_loads", [0.05, 0.1])
    mac_protocols = cfg.get("mac_protocols", ["MacTDMA", "MacCSMA", "MacALOHA", "MacCSMA_RTS"])

    sim_exe = cfg.get("sim_exe")
    exe = Path(sim_exe) if sim_exe else _default_exe()
    if not exe.is_absolute():
        exe = PROJECT_ROOT / exe
    ini = Path(cfg.get("ini_file", str(DEFAULT_INI)))
    if not ini.is_absolute():
        ini = PROJECT_ROOT / ini
    results_root = Path(cfg.get("results_root", str(DEFAULT_RESULTS_ROOT)))
    if not results_root.is_absolute():
        results_root = PROJECT_ROOT / results_root

    # NED path for -n: simulations and src
    sim_dir = PROJECT_ROOT / "simulations"
    src_dir = PROJECT_ROOT / "src"
    neds = f"{sim_dir}:{src_dir}" if sys.platform != "win32" else f"{sim_dir};{src_dir}"

    results_root.mkdir(parents=True, exist_ok=True)
    manifest_path = results_root / "manifest.csv"
    manifest_rows = []

    exp_id = 0
    for num_nodes in node_counts:
        for load in offered_loads:
            for mac in mac_protocols:
                exp_id += 1
                seed = base_seed + exp_id
                dir_name = f"{exp_id:04d}_nodes{num_nodes}_load{load}_{mac}"
                out_dir = results_root / dir_name
                out_dir.mkdir(parents=True, exist_ok=True)
                manifest_rows.append({
                    "experiment_id": exp_id,
                    "seed": seed,
                    "num_nodes": num_nodes,
                    "packet_interval": load,
                    "mac": mac,
                    "network": network,
                    "output_dir": str(out_dir),
                })
                if args.dry_run:
                    print(f"Would run: nodes={num_nodes} load={load} mac={mac} -> {out_dir}")
                    continue
                ok = run_one(
                    exe=exe,
                    ini=ini,
                    out_dir=out_dir,
                    network=network,
                    num_nodes=num_nodes,
                    mac=mac,
                    packet_interval=load,
                    sim_time_limit=sim_time_limit,
                    seed=seed,
                    neds=neds,
                )
                status = "ok" if ok else "failed"
                manifest_rows[-1]["status"] = status
                print(f"Experiment {exp_id}: {dir_name} -> {status}")

    if not args.dry_run and manifest_rows:
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["experiment_id", "seed", "num_nodes", "packet_interval", "mac", "network", "output_dir", "status"])
            w.writeheader()
            for r in manifest_rows:
                r.setdefault("status", "ok")
                w.writerow(r)
        print(f"Manifest written: {manifest_path}")

    if args.dry_run:
        print(f"Dry run: would write manifest to {manifest_path}")

    failed = sum(1 for r in manifest_rows if r.get("status") == "failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
