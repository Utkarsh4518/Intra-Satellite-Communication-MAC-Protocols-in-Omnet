# Latency metrics for time-critical TMTC in intra-satellite LiFi

This document defines the **latency-related metrics** used in the project and explains how they behave under **TDMA**, **CSMA**, and **ALOHA**. The focus is **time-critical TMTC (Telemetry, Monitoring & Telecommand)** traffic: predictability and bounded delay matter more than raw throughput.

---

## 1. Definitions of latency metrics

All metrics are **MAC-layer end-to-end delay**: time from **packet generation** (handed to the MAC) until **successful delivery** (transmission completed without collision, and in multi-hop topologies, all hops completed). Units: seconds (simulation time).

| Metric | Scalar name | Definition | Why it matters for TMTC |
|--------|-------------|------------|--------------------------|
| **Average delay** | `E2EDelayMean` | Mean of (delivery_time − generation_time) over all delivered packets. | Typical latency; useful for capacity and average response time. |
| **Worst-case delay** | `E2EDelayMax` | Maximum of (delivery_time − generation_time) over all delivered packets. | **Critical for TMTC**: upper bound on how long a telecommand or telemetry sample can take; safety and real-time loops need a known bound. |
| **Jitter** | `E2EDelayJitter` | Standard deviation of the same delay. | **Critical for TMTC**: low jitter ⇒ predictable timing; high jitter ⇒ hard to guarantee deadlines and synchronize with ground or other subsystems. |

- **Dropped packets** (collisions, retries exhausted) are **not** included in these statistics; only **delivered** packets contribute. For TMTC, the combination of **PDR** (how many packets are delivered) and **E2EDelayMax** / **E2EDelayJitter** (how predictable the delay of delivered packets is) is what matters.

---

## 2. How the metrics differ: TDMA vs CSMA vs ALOHA

### TDMA (deterministic scheduling)

- **Average delay:** Bounded and predictable. Each node has a fixed slot; delay is (slot phase + one or more frame lengths). Mean delay is close to **half a frame** plus any per-hop component; it grows with `numNodes` and `numHops` in a **deterministic** way.
- **Worst-case delay:** **Strictly bounded.** A packet generated just after the node’s slot waits at most until the next occurrence of that slot (one frame). So worst-case ≈ **one frame length** (plus propagation/processing if modeled). No unbounded backoff or retries.
- **Jitter:** **Very low.** Delay varies only by “where in the frame” the packet was generated (at most one frame difference). So jitter is on the order of the frame/slot duration, not of random backoffs or collision retries.

**Conclusion:** TDMA gives **deterministic, predictable latency** — exactly what time-critical TMTC needs.

---

### CSMA (contention with backoff and retries)

- **Average delay:** Depends on load. At low load, delay is small (short defer + one attempt). As load or hop count increases, **collisions and exponential backoff** increase mean delay. So average delay is **load- and topology-dependent** and not guaranteed.
- **Worst-case delay:** **Not bounded.** After a collision, backoff can go up to `maxBackoff`; with retries, a single packet can see several backoffs in sequence. Worst-case is “multiple retries × max backoff” plus transmission time — and in principle another collision can always occur. So **E2EDelayMax** can be large and **increases with run length** (more chances to see an extreme case).
- **Jitter:** **High under load.** Delay varies strongly: no collision ⇒ low delay; collision + backoff ⇒ much higher delay. So standard deviation is large; timing is **unpredictable**.

**Conclusion:** CSMA is **unsuitable for strict TMTC deadlines** when the network is loaded or multi-hop; average and worst-case delay and jitter are unpredictable.

---

### ALOHA (no carrier sense, random retransmit)

- **Average delay:** Similar to CSMA in that it depends on load, but typically **worse** than CSMA because there is no deferral or backoff structure — retransmits are random. So under load, mean delay is **higher** than CSMA for the same offered load.
- **Worst-case delay:** **Unbounded and worse than CSMA.** No backoff cap; a packet can in principle be retransmitted many times. Observed maximum delay can be very large and highly variable between runs.
- **Jitter:** **Highest of the three.** Delay is dominated by random retransmission timing; variance is large. **Least predictable** for TMTC.

**Conclusion:** ALOHA is the **worst choice** for time-critical TMTC: poor average, unbounded worst-case, and highest jitter.

---

## 3. Deterministic scheduling and predictability

**Deterministic scheduling** (TDMA) means:

1. **Fixed slot assignment** — each node knows exactly when it may transmit.
2. **No contention** — no collisions, so no random backoff or retransmission delay.
3. **Bounded wait** — a packet generated at time \(t\) is transmitted by the next slot for that node, at worst one frame later.

So:

- **Worst-case delay** is **bounded** by (frame length × numHops) plus slot phase.
- **Jitter** is **small** and determined only by the position of packet generation within the frame.
- **Average delay** is **predictable** from frame size and numNodes/numHops.

For **time-critical TMTC** this means:

- **Deadlines** can be set using the known worst-case (e.g. “telecommand must be executed within 2× frame length”).
- **Synchronization** with ground or other subsystems is feasible because delay variation (jitter) is small.
- **Certification / safety** arguments are easier when delay and jitter are bounded and reproducible.

By contrast, **CSMA and ALOHA** introduce randomness (collisions, backoff, retries), so:

- Worst-case delay is **not** bounded.
- Jitter is **high**.
- Predictability is **poor** — not suitable for hard real-time TMTC without over-provisioning or additional mechanisms (e.g. reserved slots or hybrid schemes).

---

## 4. Summary table (TMTC perspective)

| Metric | TDMA | CSMA | ALOHA |
|--------|------|------|--------|
| **Average delay** | Bounded, predictable | Load-dependent, grows with contention | Load-dependent, typically worse than CSMA |
| **Worst-case delay** | **Bounded** (≈ frame × numHops) | **Unbounded** (retries × backoff) | **Unbounded**, often worst |
| **Jitter** | **Low** (frame/slot scale) | **High** under load | **Highest** |
| **Predictability** | **Deterministic** | Probabilistic | Probabilistic, least predictable |

For **TMTC traffic**, TDMA is the only option that provides **deterministic, predictable latency**; CSMA and ALOHA are better suited to best-effort traffic where average throughput matters more than strict delay bounds and jitter.

---

## 5. Result scalars and how to use them

In the simulation **scalar results** (per node or aggregated):

- **E2EDelayMean** — use as “average delay” for reports and comparisons.
- **E2EDelayMax** — use as “worst-case delay”; for TDMA it should stay stable and bounded as sim time increases; for CSMA/ALOHA it can grow with run length.
- **E2EDelayJitter** — use as “jitter”; compare across MACs to show that TDMA has much lower jitter.

For **TMTC-focused** runs:

- Use the same **per-node logical load** (e.g. 20 pkts/s) and **sim-time-limit** (e.g. 50 s) across MACs.
- Compare **E2EDelayMax** and **E2EDelayJitter** across TDMA, CSMA, and ALOHA to support the claim that **deterministic scheduling is necessary for predictable, time-critical intra-satellite LiFi**.
