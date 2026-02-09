# Failure Condition Detection (Observation Only)

Failure conditions are **detected and logged** using configurable thresholds. No enforcement is applied: simulation behaviour (scheduling, discarding, routing) is unchanged. All thresholds are **assumptions** and must be set via configuration for any study.

---

## Assumptions

- **pdrFailureThreshold:** Assumed minimum acceptable packet delivery ratio. If PDR < this value, a failure is logged. Not enforced.
- **deadlineMissRateFailureThreshold:** Assumed maximum acceptable fraction of delivered packets that miss the deadline. If DeadlineMissRatio > this value, a failure is logged. Not enforced.
- **retryExhaustionRateFailureThreshold:** Assumed maximum acceptable fraction of generated packets that are dropped after retry exhaustion. If (RetriesExhausted / Generated) > this value, a failure is logged. Not enforced.

No real system requirement or standard is implied. Defaults in NED are for simulation only.

---

## How Failure States Are Detected

Detection runs once per MAC instance at the end of the run (in `finish()`).

1. **PDR below threshold**  
   - Compute PDR = Delivered / Generated (0 if Generated = 0).  
   - If Generated > 0 and PDR < `pdrFailureThreshold` → failure detected.  
   - Logged and scalar PDRFailure = 1 recorded; otherwise PDRFailure = 0.

2. **Deadline miss rate above threshold**  
   - Compute DeadlineMissRatio = DeadlineMisses / Delivered (only when Delivered > 0).  
   - If Delivered > 0 and DeadlineMissRatio > `deadlineMissRateFailureThreshold` → failure detected.  
   - Logged and scalar DeadlineMissRateFailure = 1 recorded; otherwise 0.  
   - If Delivered = 0, no deadline failure is signalled (ratio undefined).

3. **Retry exhaustion rate above threshold**  
   - Compute RetryExhaustionRate = RetriesExhausted / Generated (0 if Generated = 0).  
   - If Generated > 0 and RetryExhaustionRate > `retryExhaustionRateFailureThreshold` → failure detected.  
   - Logged and scalar RetryExhaustionRateFailure = 1 recorded; otherwise 0.

4. **AnyFailure**  
   - Scalar AnyFailure = 1 if at least one of the three conditions above is true; otherwise 0.  
   - For analysis only; not used to change behaviour.

Detection is **observation only**: it does not alter metrics, drop packets, or change MAC logic. It only evaluates the three conditions and writes log lines and scalars.

---

## Code Changes

1. **MacInterface.ned**  
   - Added parameters (all with “Assumption” in comment, observation only, not enforced):  
     - `pdrFailureThreshold` (default 0.9)  
     - `deadlineMissRateFailureThreshold` (default 0.1)  
     - `retryExhaustionRateFailureThreshold` (default 0.1)

2. **MacBase.cc**  
   - In `finish()`, after recording all other scalars: if the module has all three threshold parameters, call `logFailureConditions()`.  
   - `logFailureConditions()`:  
     - Reads the three thresholds from parameters.  
     - Computes PDR, DeadlineMissRatio, RetryExhaustionRate.  
     - Sets binary flags (0/1) for each condition and for AnyFailure.  
     - Records scalars: PDRFailure, DeadlineMissRateFailure, RetryExhaustionRateFailure, AnyFailure.  
     - For each condition that is true, emits one EV_WARN log line (see Logging format).

No other files modified. No enforcement or change to protocol or packet handling.

---

## Logging Format

**Event log (EV_WARN):**  
One line per triggered condition, prefix and format:

- PDR:  
  `[Failure detection - assumption] PDR below threshold: module=<full path> PDR=<value> threshold=<value>`
- Deadline miss rate:  
  `[Failure detection - assumption] Deadline miss rate above threshold: module=<full path> rate=<value> threshold=<value>`
- Retry exhaustion rate:  
  `[Failure detection - assumption] Retry exhaustion rate above threshold: module=<full path> rate=<value> threshold=<value>`

`<full path>` is the module’s full path (e.g. `lifihiddennode.LiFiHiddenRing.node[0].mac`). Values and thresholds are numeric. Only conditions that are true produce a line.

**Scalar output (e.g. *.sca):**  
Per run, per MAC module:

| Scalar name | Value | Meaning |
|-------------|--------|--------|
| PDRFailure | 0 or 1 | 1 if PDR < pdrFailureThreshold |
| DeadlineMissRateFailure | 0 or 1 | 1 if DeadlineMissRatio > deadlineMissRateFailureThreshold |
| RetryExhaustionRateFailure | 0 or 1 | 1 if (RetriesExhausted/Generated) > retryExhaustionRateFailureThreshold |
| AnyFailure | 0 or 1 | 1 if any of the above is 1 |

These scalars allow filtering or post-processing by failure type without interpreting results in the simulation.

---

## Configuration

In `simulations/omnetpp.ini` (or per-config):

```ini
**.mac.pdrFailureThreshold = 0.9
**.mac.deadlineMissRateFailureThreshold = 0.1
**.mac.retryExhaustionRateFailureThreshold = 0.1
```

All three are optional; if any is missing, `logFailureConditions()` is not called and no failure detection is performed.
