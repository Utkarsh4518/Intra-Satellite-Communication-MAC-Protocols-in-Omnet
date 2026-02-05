# Scalability experiments: MAC strategies in intra-satellite optical networks

## Objective

Study **scalability limits** of different MAC strategies (TDMA, CSMA, ALOHA) as the number of subsystems sharing the optical channel increases. This supports design choices for intra-satellite LiFi with multiple nodes on a shared optical bus.

## Experiment design

### Factors

| Factor | Levels | Purpose |
|--------|--------|--------|
| **MAC** | TDMA, CSMA (realistic), ALOHA | Compare scheduled vs contention-based |
| **numNodes** | 4, 8, 12, 16 | Scale system size (subsystems on shared channel) |

### Fixed: per-node traffic

- **Per-node rate**: 20 packets/s (same for all MACs).
- **CSMA / ALOHA**: packet interval = 0.05 s per node.
- **TDMA**: slot time = `1 / (20 × numNodes)` so each node gets 20 slots per second in a round-robin frame.
- **Total offered load** = `numNodes × 20` pkts/s → load scales with system size.

### Simulation

- **Network**: `LiFiHiddenRing` (single shared `OpticalChannel`).
- **Run length**: 50 s per config (for stable PDR and delay statistics).
- **Configs**: `Scalability-{TDMA|CSMA|ALOHA}-{4|8|12|16}` in `simulations/omnetpp.ini`.

## How to run

1. Build the project in the OMNeT++ IDE (or with `opp_makemake` + `make`).
2. In the **Simulation** dialog, choose **Config** (e.g. `Scalability-CSMA-8`).
3. Run; results go to the configured results/output directory.
4. Repeat for each of the 12 configs (3 MACs × 4 node counts).

Optional: run from command line with different configs and collect scalars (e.g. into CSV) for batch analysis.

## Metrics to collect

From **scalar results** (per node; aggregate or average as needed):

| Metric | Meaning | What to look for |
|--------|--------|-------------------|
| **PDR** | Packet delivery ratio (delivered / generated) | Drop as contention grows → contention limit |
| **E2EDelayMean** | Mean MAC delay (gen → delivery) | CSMA/ALOHA mean delay grows with N |
| **E2EDelayMax** | Worst-case delay | TMTC predictability; TDMA bounded |
| **E2EDelayJitter** | Std dev of delay | TDMA low; CSMA/ALOHA high under load |
| **Collisions** | Collision count per node | Contention; should increase with N for CSMA/ALOHA |
| **RetriesExhausted** | Packets dropped after max retries (CSMA) | Realistic CSMA degradation |
| **TX_Attempts** | Transmission attempts per node | vs Delivered → efficiency |

## Analysis guide

### 1. When do contention-based protocols degrade?

- **PDR**: Plot PDR vs `numNodes` for each MAC.
  - **TDMA**: Should stay near 1.0 (no contention).
  - **CSMA**: Expect PDR to fall as N increases (more collisions, more retries, then retries exhausted).
  - **ALOHA**: Expect earlier and steeper PDR drop (no carrier sense, no backoff).
- **Threshold**: Note the **smallest N** where CSMA (or ALOHA) PDR falls below a target (e.g. 0.95 or 0.9). That is a practical “contention limit” for that load.

### 2. Scalability comparison

- **TDMA**: Throughput and PDR scale with N (fixed per-node rate); delay and jitter stay predictable.
- **CSMA**: Useful up to some N; beyond that, collisions and retries dominate → use TDMA or hybrid.
- **ALOHA**: Typically degrades soonest; good for very low load or few nodes only.

### 3. Delay and jitter (TMTC-style requirements)

- **E2EDelayMean / Max / Jitter** vs `numNodes`:
  - TDMA: stable, low jitter (deterministic slots).
  - CSMA/ALOHA: mean and max delay and jitter grow with N (backoff, retries, contention).
- Use this to argue that **TDMA scales better** for latency-sensitive, predictable TMTC in intra-satellite optical nets.

### 4. Suggested plots (for report/slides)

1. **PDR vs numNodes** (one curve per MAC).
2. **E2EDelayMean vs numNodes** (one curve per MAC).
3. **E2EDelayJitter vs numNodes** (one curve per MAC).
4. **Collisions (or RetriesExhausted) vs numNodes** for CSMA/ALOHA.

## Conclusion framing

- **Contention-based (CSMA, ALOHA)** degrade at some **N** for fixed per-node load; that N depends on MAC and parameters.
- **TDMA** maintains PDR and predictable delay/jitter as N increases under the same per-node rate.
- For **intra-satellite optical networks** with multiple subsystems on one channel, these experiments show **at what point** to prefer TDMA (or a TDMA–CSMA hybrid) over pure contention-based access.
