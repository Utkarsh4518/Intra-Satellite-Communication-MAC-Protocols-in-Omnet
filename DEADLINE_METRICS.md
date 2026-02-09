# Deadline Metrics (Observation Only)

Packets can be associated with a **configurable hypothetical deadline** for the purpose of observing and recording latency-sensitive behaviour. Deadlines are **not** used for scheduling, prioritization, or discarding; the MAC is unchanged. Only observation and recording are added.

---

## Assumption

**Deadline is hypothetical.** The parameter `deadline` (seconds) is an assumed maximum acceptable delay for each packet. It is used solely to classify delivered packets as "within deadline" or "deadline miss" and to record counts. No real system requirement or standard is implied. The value must be set via configuration for any study; default in NED is for simulation only.

---

## Metric Definitions

| Metric | Definition | Unit |
|--------|------------|------|
| **deadline** | Configurable parameter: hypothetical maximum acceptable delay from packet generation to delivery. A delivered packet is a **deadline miss** if (delivery time − generation time) > deadline. | s |
| **DeadlineMisses** | Number of delivered packets whose delay exceeded the configured deadline. | count |
| **DeadlineMissRatio** | DeadlineMisses / Delivered. Undefined when Delivered = 0; not recorded in that case. | ratio [0, 1] |

Only **delivered** packets are considered. Packets that are never delivered (e.g. retries exhausted, lost) are not counted as deadline misses; they are already reflected in PDR and RetriesExhausted.

---

## Code Changes

1. **MacInterface.ned**  
   - Added parameter: `deadline` (volatile double, default 1.0). Comment states: assumption, observation only, not used for scheduling or discarding.

2. **MacBase.cc**  
   - Added member: `deadlineMisses` (int).  
   - In `recordDelivery(genTime)`: after computing delay `d`, if the module has a `deadline` parameter and `delay > deadline`, increment `deadlineMisses`.  
   - In `finish()`: `recordScalar("DeadlineMisses", deadlineMisses)`; if `delivered > 0`, `recordScalar("DeadlineMissRatio", (double)deadlineMisses / delivered)`.

No other files modified. MAC scheduling and packet handling are unchanged; packets are never discarded or reordered based on the deadline.

---

## Where Deadline Violations Are Logged

- **Scalar results (OMNeT++ output):**  
  For each MAC instance (per node), the following are written at the end of the run:
  - **DeadlineMisses**: total number of delivered packets that exceeded the configured deadline.
  - **DeadlineMissRatio**: fraction of delivered packets that missed the deadline (only if Delivered > 0).

- **When the check is performed:**  
  In `MacBase::recordDelivery(simtime_t genTime)`, which is called from each MAC (CSMA, TDMA, ALOHA, CSMA_RTS) when a packet is successfully delivered. At that point, delay = simTime() − genTime; if delay > deadline, `deadlineMisses` is incremented. There is no per-packet log or event; only the aggregate counts are recorded in the scalar output.

- **Configuration:**  
  Set `**.mac.deadline = <value>` in `simulations/omnetpp.ini` (e.g. 0.5 or 1.0). Same deadline is used for all packets at that node.

---

## Summary

- **Parameter:** `deadline` (s), configurable, hypothetical.  
- **Observation:** On each delivery, if delay > deadline, increment `deadlineMisses`.  
- **Recording:** Scalars `DeadlineMisses` and `DeadlineMissRatio` in the standard OMNeT++ scalar results.  
- **No enforcement:** No scheduling, prioritization, or discarding of packets based on deadlines.
