#!/usr/bin/env python3
"""
Rule-based MAC selection helper. Deterministic; first match wins.
Not an optimizer; no ML. Returns exact reason string for the matching rule.
"""

import argparse
import sys

# Numeric offered_load mapping: >= 0.1 -> low, >= 0.05 -> medium, < 0.05 -> high
LOAD_LOW_THRESHOLD = 0.1
LOAD_MEDIUM_THRESHOLD = 0.05


def normalize_load(offered_load):
    if isinstance(offered_load, (int, float)):
        if offered_load >= LOAD_LOW_THRESHOLD:
            return "low"
        if offered_load >= LOAD_MEDIUM_THRESHOLD:
            return "medium"
        return "high"
    s = str(offered_load).strip().lower()
    if s in ("low", "medium", "high"):
        return s
    return "medium"


def select_mac_with_reason(latency_sensitivity, node_count, offered_load):
    """
    Rule evaluation in order; first match wins. Returns (MAC string, reason string).
    """
    sens = str(latency_sensitivity).strip().lower()
    if sens not in ("high", "low"):
        sens = "low"
    n = int(node_count)
    load = normalize_load(offered_load)

    # 1. latency_sensitivity == "high" -> MacTDMA
    if sens == "high":
        return ("MacTDMA", "Latency critical -> bounded delay")

    # 2. offered_load == "high" -> MacTDMA
    if load == "high":
        return ("MacTDMA", "High load -> avoid contention")

    # 3. node_count >= 9 -> MacTDMA
    if n >= 9:
        return ("MacTDMA", "Many nodes -> contention-based MACs degrade")

    # 4. latency_sensitivity == "low" AND node_count <= 4 AND offered_load == "low" -> MacCSMA
    if sens == "low" and n <= 4 and load == "low":
        return ("MacCSMA", "Low contention, relaxed latency")

    # 5. latency_sensitivity == "low" AND node_count <= 8 AND offered_load == "low or medium" -> MacCSMA_RTS
    if sens == "low" and n <= 8 and load in ("low", "medium"):
        return ("MacCSMA_RTS", "Moderate contention, hidden-node")

    # 6. default -> MacTDMA
    return ("MacTDMA", "Default to deterministic MAC")


def select_mac(latency_sensitivity, node_count, offered_load):
    mac, _ = select_mac_with_reason(latency_sensitivity, node_count, offered_load)
    return mac


def main():
    ap = argparse.ArgumentParser(description="Rule-based MAC selection (deterministic).")
    ap.add_argument("latency_sensitivity", choices=["high", "low"])
    ap.add_argument("node_count", type=int)
    ap.add_argument("offered_load", help="'low'|'medium'|'high' or packet_interval (e.g. 0.05)")
    args = ap.parse_args()
    try:
        load_arg = float(args.offered_load)
    except ValueError:
        load_arg = args.offered_load
    mac, reason = select_mac_with_reason(args.latency_sensitivity, args.node_count, load_arg)
    print(mac)
    print("# " + reason)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
