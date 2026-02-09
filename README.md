# Intra-Satellite Communication MAC Protocols in OMNeT++

A discrete-event simulation project that evaluates **MAC (Medium Access Control) protocols** for **intra-satellite LiFi (Light Fidelity)** communication using OMNeT++.

## What This Project Does

Inside a satellite, multiple subsystems (e.g. payload, power, attitude control) often share a single optical wireless link. MAC choice matters because the shared medium and time-critical traffic (e.g. telemetry and telecommand, TMTC) make contention, latency, and reliability directly dependent on the access scheme. This project simulates that shared optical channel and compares how different MAC protocols perform when several nodes contend for the medium—including under **hidden-node** conditions where nodes cannot sense each other’s transmissions. The goal is to support MAC selection reasoning: which strategy (TDMA, CSMA, or ALOHA) scales and gives predictable latency under the modeled conditions.

## What The Simulation Models

- **Shared optical channel** — One `OpticalChannel` module that all nodes use. Simultaneous transmissions cause collisions (detected and reported back to senders).
- **Nodes** — Each node has a configurable MAC and generates packets at a fixed rate (e.g. 20 packets/s per node). Traffic load scales with the number of nodes.
- **Topologies** — Same logical “shared medium” is used in three network shapes for configuration and reporting: **Ring**, **Star**, and **Bus**. Ring uses a 2-hop path per packet; Star and Bus use 1 hop, so you can compare how hop count affects delay and contention.
- **MAC protocols** — TDMA (fixed time slots), CSMA (carrier sense, exponential backoff, retries), pure ALOHA (random retransmit), and CSMA with RTS/CTS (optimistic). Each records per-node metrics: generated/delivered packets, collisions, retries exhausted, PDR, and end-to-end delay (mean, max, jitter).

You can vary the number of nodes (4, 8, 12, 16), switch topologies (Ring vs Star vs Bus), and compare protocols under the same offered load to study scalability and the impact of deterministic vs contention-based access.

**Scope and non-goals.** This project does **not** model: real mission or standards (e.g. CCSDS) compliance, synchronization cost, pointing or alignment errors, or detailed physical-layer effects. The channel and traffic are abstracted.

**Assumptions.** The following are assumed and not mission-validated: periodic or fixed-rate traffic per node; latency sensitivity and failure/trend thresholds are hypothetical inputs; no sync or slot-acquisition cost; abstract optical channel (collision detection only).

## Protocols Compared

| Protocol     | Type             | Collision handling   |
| ------------ | ---------------- | -------------------- |
| **TDMA**     | Deterministic    | Slot-based, no contention |
| **CSMA**     | Contention-based | Exponential backoff, retry limit |
| **ALOHA**    | Contention-based | Random retransmit    |
| **CSMA_RTS** | Contention-based | RTS/CTS (optimistic model) |

## Project Structure

```
├── src/
│   ├── LiFiHiddenRing.ned    # Ring network (numHops=2)
│   ├── LiFiHiddenStar.ned    # Star network (numHops=1)
│   ├── LiFiHiddenBus.ned     # Bus network (numHops=1)
│   ├── Node.ned              # Node with pluggable MAC
│   ├── OpticalChannel.cc/ned # Shared medium, collision detection
│   ├── package.ned
│   └── mac/
│       ├── MacBase.cc        # Base class, metrics (PDR, delay, jitter)
│       ├── MacTDMA.cc        # Time Division Multiple Access
│       ├── MacCSMA.cc        # CSMA with backoff and retries
│       ├── MacALOHA.cc       # Pure ALOHA
│       ├── MacCSMA_RTS.cc    # CSMA with RTS/CTS
│       └── *.ned             # MAC module definitions
├── simulations/
│   └── omnetpp.ini           # Simulation configs (Ring/Star/Bus, scalability, topology)
├── EXPERIMENTS.md            # Scalability experiment design and metrics
├── REPRODUCIBILITY.md        # Deterministic runs, seed per config
├── TOPOLOGY_ANALYSIS.md      # Star vs Ring, hop count, MAC ranking
└── LATENCY_METRICS.md        # Delay/jitter definitions, TMTC focus
```

## Metrics (Per Node)

- **Generated** — Packets offered to the MAC  
- **TX_Attempts** — Transmission attempts (including retries)  
- **Collisions** — Collision count  
- **Delivered** — Successfully delivered packets  
- **RetriesExhausted** — Packets dropped after max retries (CSMA)  
- **PDR** — Packet delivery ratio (Delivered / Generated)  
- **AvgTxAttemptsPerDelivery** — Channel uses per delivered packet (reflects hop count)  
- **E2EDelayMean** — Mean MAC delay (generation to delivery)  
- **E2EDelayMax** — Worst-case delay  
- **E2EDelayJitter** — Standard deviation of delay  

## Project Output

Each run produces **scalar results** (one set per node, plus network-level if aggregated):

- **Scalar files** — OMNeT++ writes scalars (e.g. `*.sca`) into the results directory configured in the IDE. Each node records: Generated, TX_Attempts, Collisions, Delivered, RetriesExhausted, PDR, AvgTxAttemptsPerDelivery, E2EDelayMean, E2EDelayMax, E2EDelayJitter.
- **What you get per run** — A snapshot of how that MAC performed for the chosen config (node count, topology, run length). By running multiple configs (e.g. Scalability-TDMA-4/8/12/16, Scalability-CSMA-4/8/12/16, Topology-Star-TDMA-8 vs Topology-Ring-TDMA-8), you obtain comparable data to plot PDR vs node count, delay/jitter vs protocol, and topology impact.

No GUI charts are generated by default; you use the scalar data in the OMNeT++ Result Analysis tool or export to CSV/other tools for plotting and reporting.

## What The Project Gives You

This framework can inform engineering decisions such as MAC tradeoff reasoning, scalability and load limits, and latency/reliability risk under the stated assumptions. It provides:

- **Protocol comparison** — Side-by-side PDR, delay, and jitter for TDMA, CSMA, and ALOHA under the same offered load and topology, so you can rank protocols for reliability and latency.
- **Scalability** — How each MAC behaves as the number of nodes (4, 8, 12, 16) increases with fixed per-node load. You can identify at which point contention-based protocols start to degrade (e.g. PDR drop, high retries exhausted).
- **Topology impact** — Star (1 hop) vs Ring (2 hops) comparison: more hops mean more channel uses per packet and higher contention, so you can see whether MAC conclusions hold across topologies (see `TOPOLOGY_ANALYSIS.md`).
- **Latency and predictability** — E2EDelayMean, E2EDelayMax, and E2EDelayJitter support arguments about time-critical TMTC: which MAC gives bounded delay and low jitter (see `LATENCY_METRICS.md`).
- **Reusable setup** — A clean OMNeT++ model (shared optical channel, pluggable MACs, multiple configs) that you can extend (e.g. more MACs, different traffic, or physical-layer effects).

**Limitations.** This project does **not** replace mission or standards validation, does not certify compliance, and does not support deployment or safety decisions. Conclusions hold only under the stated assumptions and modeled scenarios.

## Final Conclusion

Under the modeled assumptions and metrics:

- **TDMA** provides **deterministic, collision-free** access: PDR stays at 1, delay and jitter are **bounded and predictable**, and performance scales with node count for the same per-node rate. It is the **preferred MAC for time-critical TMTC** in this setup when deadlines and latency guarantees matter.
- **CSMA** and **ALOHA** are **contention-based**: under hidden-node conditions and as the number of nodes or hops increases, collisions and retries grow, so **PDR drops**, **delay and jitter become large and unpredictable**, and **retries exhausted** increase. They are suitable for best-effort traffic but **not** for strict TMTC requirements without over-provisioning or hybrid schemes.
- **Topology** (Star vs Ring) does not reverse the ranking (TDMA remains best) but **amplifies** the gap: multi-hop (Ring) worsens contention-based performance more than single-hop (Star), reinforcing the case for **deterministic scheduling** in ring-like or multi-hop intra-satellite optical networks.

**In short:** for the modeled intra-satellite shared channel, **TDMA is the recommended MAC** when the focus is scalability, predictable latency, and reliable delivery; contention-based protocols degrade under load and are less suitable for time-critical TMTC.

## How To Run

Runs are deterministic for a given config (fixed seed per config). See **`REPRODUCIBILITY.md`** for seed-to-config mapping. One-command batch path: from project root, `python scripts/run_sweep.py` (see `SWEEP.md`).

Single run (IDE):  
1. **Open** the project in the OMNeT++ IDE.  
2. **Build** the project (e.g. Build → Build Project).  
3. **Select config** in the Run dialog (e.g. `Scalability-CSMA-8`, `Topology-Star-TDMA-8`, `Ring4`, `Star8`).  
4. **Run** the simulation; inspect **scalar results** (PDR, E2EDelayMean, E2EDelayMax, E2EDelayJitter, etc.) in the results folder or Analysis tool.

To change the default MAC in `omnetpp.ini`, set e.g. `**.macType = "MacTDMA"` (or `MacCSMA`, `MacALOHA`, `MacCSMA_RTS`).

A **rule-based MAC selection helper** suggests a preferred MAC from latency sensitivity, node count, and offered load. This is a deterministic, rule-based helper intended to support MAC selection reasoning. It does not guarantee optimality. See **`MAC_SELECTION.md`** for the rule table and validation examples.

**CLI:** `python scripts/mac_select.py <latency_sensitivity> <node_count> <offered_load>`

Example: `python scripts/mac_select.py high 4 0.1` → MacTDMA; `python scripts/mac_select.py low 4 low` → MacCSMA.

### Automated sweeps

Scripted batch runs over **node count**, **offered load**, and **MAC protocol** with unique experiment IDs and organized output under `results/sweep/`. No manual execution. See **`SWEEP.md`** for directory structure, usage, and **`scripts/sweep_config_example.yaml`** for an example configuration. Run from project root: `python scripts/run_sweep.py` (optionally with `--dry-run`).

**Post-processing** adds qualitative failure trends (latency high, collision-dominated, retry exhaustion onset) with clear separation between **observations** and **interpretations**; no curve fitting or extrapolation. See **`TREND_INDICATORS.md`**. Run: `python scripts/postprocess_sweep.py`.

## Requirements

- OMNeT++ 6.x  
- C++14 or later  

## License

MIT
