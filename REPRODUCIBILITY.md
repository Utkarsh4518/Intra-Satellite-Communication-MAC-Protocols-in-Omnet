# Deterministic and Reproducible Experiments

The simulation is set up so that the same configuration always produces identical results. No protocol logic or metrics were changed; only seed control was added in the configuration.

## Code Changes

**No C++ or NED code changes.** All randomness in the model (MAC packet inter-arrival, defer, backoff, retransmit delays) uses OMNeT++’s global RNG (`uniform()`, `exponential()`). That RNG is seeded from the ini file. Controlling the seed in ini is enough for reproducibility.

**Ini changes (simulations/omnetpp.ini):**

- **[General]:** `seed-set = 0` so the default run uses a fixed seed.
- **Each [Config ...]:** `seed-set = N` with a unique integer N (1–30) for that config. Config-specific entries override [General], so each experiment has a fixed seed.

Protocol logic and recorded metrics are unchanged.

## Experiment ID to Seed Mapping

Experiment ID is the seed value used for that configuration. Mapping: **seed = experiment ID** (1:1).

| Experiment ID (seed) | Config name |
|----------------------|-------------|
| 0 | (default [General] when no config selected) |
| 1 | Ring4 |
| 2 | Ring8 |
| 3 | Ring12 |
| 4 | Ring16 |
| 5 | Star4 |
| 6 | Star8 |
| 7 | Star12 |
| 8 | Star16 |
| 9 | Bus4 |
| 10 | Bus8 |
| 11 | Bus12 |
| 12 | Bus16 |
| 13 | Scalability-TDMA-4 |
| 14 | Scalability-TDMA-8 |
| 15 | Scalability-TDMA-12 |
| 16 | Scalability-TDMA-16 |
| 17 | Scalability-CSMA-4 |
| 18 | Scalability-CSMA-8 |
| 19 | Scalability-CSMA-12 |
| 20 | Scalability-CSMA-16 |
| 21 | Scalability-ALOHA-4 |
| 22 | Scalability-ALOHA-8 |
| 23 | Scalability-ALOHA-12 |
| 24 | Scalability-ALOHA-16 |
| 25 | Topology-Star-TDMA-8 |
| 26 | Topology-Ring-TDMA-8 |
| 27 | Topology-Star-CSMA-8 |
| 28 | Topology-Ring-CSMA-8 |
| 29 | Topology-Star-ALOHA-8 |
| 30 | Topology-Ring-ALOHA-8 |

To add a new experiment: assign a new, unused experiment ID (seed) in its [Config ...] section, e.g. `seed-set = 31`.

## How Reproducibility Is Guaranteed

1. **Single RNG:** All random draws (MAC packet generation, defer, backoff, retransmit) use the simulation kernel’s default RNG, which is seeded once at startup from `seed-set` in the active ini configuration.

2. **Seed fixed per config:** Each [Config ...] sets `seed-set` to a fixed integer. When you run that config, OMNeT++ initializes the RNG with that seed. No other code path changes the seed during the run.

3. **Deterministic execution:** For a given seed, the OMNeT++ RNG produces a fixed sequence of numbers. Same network, same parameters, same sim-time-limit, and same seed imply the same event order and the same outcomes (same scalars).

4. **Same configuration ⇒ same results:** “Same configuration” means the same [Config] (or [General]) and the same ini parameters. That implies the same `seed-set`, network, numNodes, macType, packetInterval, etc. So the same configuration always yields the same seed and the same results.

5. **No external nondeterminism:** The model does not use wall-clock time, thread scheduling, or other external sources of randomness. The only source of randomness is the seeded RNG.

**Summary:** Same config ⇒ same seed ⇒ same RNG sequence ⇒ same events and same scalar results. Reproducibility is guaranteed by fixing the seed per experiment in the ini and not changing protocol or metrics code.
