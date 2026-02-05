# Intra-Satellite Communication MAC Protocols in OMNeT++

Simulation-based evaluation of MAC protocols for intra-satellite LiFi networks in OMNeT++.

## Overview

Compares TDMA, CSMA, and ALOHA on a shared optical channel under hidden-node conditions:

| Protocol     | Type             | Collision handling   |
| ------------ | ---------------- | -------------------- |
| **TDMA**     | Deterministic    | Slot-based           |
| **CSMA**     | Contention-based | Backoff, retries     |
| **ALOHA**    | Contention-based | Random retransmit    |
| **CSMA_RTS** | Contention-based | RTS/CTS (optimistic) |

## Structure

- `src/` — NED networks (Ring, Star, Bus), `OpticalChannel`, Node, MAC modules
- `src/mac/` — MacBase, MacTDMA, MacCSMA, MacALOHA, MacCSMA_RTS
- `simulations/omnetpp.ini` — Configs (node count, topology, scalability, topology comparison)
- `EXPERIMENTS.md` — Scalability experiment design and metrics
- `TOPOLOGY_ANALYSIS.md` — Star vs ring and hop count
- `LATENCY_METRICS.md` — Delay/jitter definitions and TMTC focus

## Metrics

Per-node: Generated, TX_Attempts, Collisions, Delivered, RetriesExhausted, PDR, AvgTxAttemptsPerDelivery, E2EDelayMean, E2EDelayMax, E2EDelayJitter.

## Run

1. Open in OMNeT++ IDE and build.
2. In Run → Config select a config (e.g. `Scalability-CSMA-8`, `Topology-Star-TDMA-8`).
3. Run; inspect scalars in results.

## Requirements

OMNeT++ 6.x, C++14 or later.

## License

MIT
