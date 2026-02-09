#!/usr/bin/env python3
"""
Post-process sweep results: extract qualitative failure trends.

- Observations: aggregated metrics from scalars (no curve fitting, no extrapolation).
- Interpretations: trend indicators (latency unbounded, collision-dominated, retry exhaustion onset).
Clear separation between observation and interpretation; no claims of optimality.

Usage:
  From project root: python scripts/postprocess_sweep.py [sweep_results_root]
  Default sweep_results_root: results/sweep
  Trend config: scripts/trend_config.yaml or scripts/trend_config_example.yaml
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from read_scalars import read_scalars_from_dir

PROJECT_ROOT = _SCRIPT_DIR.parent
DEFAULT_SWEEP_ROOT = PROJECT_ROOT / "results" / "sweep"


def load_yaml(path: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        out = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#")[0].strip()
            if ":" not in line or not line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if k == "latency_unbounded_threshold_sec":
                out[k] = float(v)
            elif k == "collision_dominated_ratio_threshold":
                out[k] = float(v)
            elif k == "retry_exhaustion_onset_ratio_threshold":
                out[k] = float(v)
        return out


def aggregate_scalars(scalar_rows: list[dict]) -> dict:
    """Compute per-run observations from scalar list. Observation only; no interpretation."""
    by_name = {}
    for r in scalar_rows:
        n = r["name"]
        if n not in by_name:
            by_name[n] = []
        by_name[n].append(r["value"])

    total_gen = sum(by_name.get("Generated", [0]))
    total_del = sum(by_name.get("Delivered", [0]))
    total_coll = sum(by_name.get("Collisions", [0]))
    total_tx = sum(by_name.get("TX_Attempts", [0]))
    total_re = sum(by_name.get("RetriesExhausted", [0]))
    e2e_max_list = by_name.get("E2EDelayMax", [])
    pdr_list = by_name.get("PDR", [])

    obs = {
        "obs_total_generated": total_gen,
        "obs_total_delivered": total_del,
        "obs_total_collisions": total_coll,
        "obs_total_tx_attempts": total_tx,
        "obs_total_retries_exhausted": total_re,
        "obs_max_e2e_delay_sec": max(e2e_max_list) if e2e_max_list else None,
        "obs_mean_pdr": (sum(pdr_list) / len(pdr_list)) if pdr_list else None,
    }
    # Ratios (observations; avoid div-by-zero)
    obs["obs_collision_ratio"] = (total_coll / total_tx) if total_tx else None
    obs["obs_retry_exhaustion_ratio"] = (total_re / total_gen) if total_gen else None
    return obs


def apply_interpretation(obs: dict, cfg: dict) -> dict:
    """
    Map observations to qualitative trend indicators.
    Criteria are threshold-based only; no curve fitting or extrapolation.
    """
    lat_th = float(cfg.get("latency_unbounded_threshold_sec", 2.0))
    coll_th = float(cfg.get("collision_dominated_ratio_threshold", 0.3))
    re_th = float(cfg.get("retry_exhaustion_onset_ratio_threshold", 0.05))

    max_delay = obs.get("obs_max_e2e_delay_sec")
    coll_ratio = obs.get("obs_collision_ratio")
    re_ratio = obs.get("obs_retry_exhaustion_ratio")

    interpret = {
        "interpret_latency_high": 1 if max_delay is not None and max_delay > lat_th else 0,
        "interpret_collision_dominated": 1 if coll_ratio is not None and coll_ratio > coll_th else 0,
        "interpret_retry_exhaustion_onset": 1 if re_ratio is not None and re_ratio > re_th else 0,
    }
    interpret["interpret_any_trend"] = 1 if any(interpret.values()) else 0
    return interpret


def main() -> None:
    ap = argparse.ArgumentParser(description="Post-process sweep: observations + qualitative trend indicators.")
    ap.add_argument("sweep_root", nargs="?", default=None, help="Sweep results root (default: results/sweep)")
    ap.add_argument("--trend-config", default=None, help="Path to trend config YAML")
    ap.add_argument("--no-header-comment", action="store_true", help="Do not write observation/interpretation header comment")
    args = ap.parse_args()

    sweep_root = Path(args.sweep_root) if args.sweep_root else DEFAULT_SWEEP_ROOT
    if not sweep_root.is_absolute():
        sweep_root = PROJECT_ROOT / sweep_root
    manifest_path = sweep_root / "manifest.csv"
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    # Trend config
    trend_path = Path(args.trend_config) if args.trend_config else None
    if not trend_path:
        for name in ("trend_config.yaml", "trend_config_example.yaml"):
            p = PROJECT_ROOT / "scripts" / name
            if p.exists():
                trend_path = p
                break
    if not trend_path or not trend_path.exists():
        print("No trend_config.yaml or trend_config_example.yaml found.", file=sys.stderr)
        sys.exit(1)
    trend_cfg = load_yaml(trend_path)

    # Read manifest
    rows = []
    with open(manifest_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    out_path = sweep_root / "trends.csv"
    obs_cols = [
        "obs_total_generated", "obs_total_delivered", "obs_total_collisions",
        "obs_total_tx_attempts", "obs_total_retries_exhausted",
        "obs_max_e2e_delay_sec", "obs_mean_pdr",
        "obs_collision_ratio", "obs_retry_exhaustion_ratio",
    ]
    interp_cols = [
        "interpret_latency_high", "interpret_collision_dominated",
        "interpret_retry_exhaustion_onset", "interpret_any_trend",
    ]
    manifest_cols = ["experiment_id", "seed", "num_nodes", "packet_interval", "mac", "network", "output_dir"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        if not args.no_header_comment:
            f.write("# Observation columns (obs_*): aggregated scalars; no fitting or extrapolation.\n")
            f.write("# Interpretation columns (interpret_*): qualitative trend flags from thresholds; not optimality claims.\n")
        w = csv.DictWriter(f, fieldnames=manifest_cols + obs_cols + interp_cols, extrasaction="ignore")
        w.writeheader()

        for m in rows:
            out_dir = m.get("output_dir", "")
            if not out_dir:
                continue
            path = Path(out_dir)
            if not path.is_absolute():
                path = PROJECT_ROOT / path
            scalar_rows = read_scalars_from_dir(path)
            if not scalar_rows:
                # Write row with empty observations/interpretations
                out = {k: m.get(k, "") for k in manifest_cols}
                for c in obs_cols + interp_cols:
                    out[c] = ""
                w.writerow(out)
                continue
            obs = aggregate_scalars(scalar_rows)
            interp = apply_interpretation(obs, trend_cfg)
            out = {k: m.get(k, "") for k in manifest_cols}
            for k, v in obs.items():
                out[k] = v if v is not None else ""
            for k, v in interp.items():
                out[k] = v
            w.writerow(out)

    print(f"Wrote {out_path}")
    # Summary of trend counts
    with open(out_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader((line for line in f if not line.startswith("#")), restval="")
        interp_counts = {c: 0 for c in interp_cols}
        n = 0
        for row in r:
            n += 1
            for c in interp_cols:
                try:
                    if int(row.get(c, 0)) == 1:
                        interp_counts[c] += 1
                except ValueError:
                    pass
    print("Trend indicator counts (interpretation only):")
    for c in interp_cols:
        print(f"  {c}: {interp_counts[c]} / {n}")


if __name__ == "__main__":
    main()
