# Metrics Collection

All metrics are computed **per experiment** (one simulation run). No averaging or aggregation across experiments is performed. Values are recorded as collected; no normalization or interpretation is applied.

---

## Metric Collection Logic

Each MAC instance (per node) maintains the following over the run:

| Metric | Collection logic | Scope |
|--------|------------------|--------|
| **Maximum end-to-end latency** | On each successful delivery, delay = simTime() − generation time. Track running maximum over all deliveries in the run. At finish, record that maximum. | Per run, per module |
| **Latency jitter** | On each successful delivery, accumulate delay and delay². At finish, variance = (sum delay² / N) − (sum delay / N)²; jitter = √variance. N = number of delivered packets in the run. | Per run, per module |
| **Packet delivery ratio** | Count of generated packets and count of delivered packets in the run. PDR = Delivered / Generated (0 if Generated = 0). | Per run, per module |
| **Collision count** | Increment on each collision event in the run. Record total at finish. | Per run, per module |
| **Retries exhausted** | Increment when a packet is dropped after max retries (CSMA). Record total at finish. | Per run, per module |

**Worst-case (maximum latency):** Updated only when a delivery occurs; comparison is (current delay > running max). The value written at end of run is the maximum over all deliveries in that run. Not combined with other runs.

**Jitter:** Computed from the sample of delays of all delivered packets in the run. Single run only.

**PDR, Collisions, Retries exhausted:** Simple counts over the run. No cross-run aggregation.

---

## Output Format

**Where:** OMNeT++ scalar output (e.g. `*.sca` or as configured in the IDE).

**Structure:** One scalar record per (run, module, scalar name). Each experiment (one config, one run) produces one set of scalar rows for each module instance (e.g. one row per node’s MAC).

**Scalar names written:**

| Scalar name | Type | Description |
|-------------|------|-------------|
| E2EDelayMax | double | Maximum end-to-end latency (s) in this run. Omitted if Delivered = 0. |
| E2EDelayJitter | double | Standard deviation of delay (s) in this run. Omitted if Delivered = 0. |
| PDR | double | Packet delivery ratio [0,1] in this run. |
| Collisions | int | Collision count in this run. |
| RetriesExhausted | int | Retries exhausted count in this run. |

Additional scalars (Generated, TX_Attempts, Delivered, E2EDelayMean, DeadlineMisses, etc.) are written by the same logic; the five above are the ones explicitly required for worst-case and related behaviour.

**Per experiment:** Each run has its own run ID. Scalars are keyed by run ID and module ID. To obtain worst-case or other metrics for one experiment, use the scalars for that run only. Do not average E2EDelayMax or other scalars across runs unless done explicitly in post-processing outside this simulation.

---

## Code Location

- **MacBase.cc:** `recordDelivery(genTime)` updates running max delay and delay sums. `finish()` computes and records all scalars. No aggregation across runs; each run is independent.
