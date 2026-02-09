# Traffic Profiles

Explicit traffic profiles represent TMTC-style behaviour in a parameterized way. All values are configurable; no real standards or fixed numerical requirements are implied. MAC behaviour (contention, backoff, retries) is unchanged; only the pattern of packet generation is affected.

---

## Traffic Model Definitions

### 1. Periodic low-rate traffic (`trafficProfile = "periodic"`)

- **Description:** One packet is generated per node at a fixed mean interval. Intended to represent steady, low-rate traffic (e.g. housekeeping-style).
- **Parameters:**
  - `packetInterval` (s): mean time between packet generations per node. First packet is scheduled at a random time in `[0, packetInterval]`; each subsequent packet is scheduled at `currentTime + packetInterval` after the previous generation (after the packet is delivered or dropped).
- **Assumptions:**
  - Packet generation is independent of channel outcome (next packet is scheduled after the previous one is done, using the same interval).
  - No reference to specific bit rates or frame formats; only inter-packet time is modelled.

### 2. Periodic traffic with occasional burst events (`trafficProfile = "periodicWithBurst"`)

- **Description:** Two concurrent processes: (1) periodic low-rate stream as above; (2) a burst process that, at fixed intervals, generates a short burst of packets. Intended to represent steady traffic plus occasional burst events (e.g. events or command batches).
- **Parameters:**
  - `baseInterval` (s): interval between periodic (low-rate) packet generations.
  - `burstInterval` (s): time between the start of successive bursts.
  - `burstSize`: number of packets in each burst.
  - `interPacketInBurst` (s): time between the start of consecutive packets within a burst.
- **Behaviour:**
  - Periodic stream: first packet at uniform(0, baseInterval); then next at `currentTime + baseInterval` after each periodic generation.
  - Burst stream: first burst at `burstInterval` from sim start; then every `burstInterval` seconds, `burstSize` packets are scheduled at times `burstStart + k * interPacketInBurst` for k = 0 .. burstSize-1.
  - Both streams run independently; no coupling between periodic and burst packets.
- **Assumptions:**
  - Burst and periodic processes are independent (no mutual exclusion or prioritization).
  - Burst size and spacing are fixed per run; no randomisation of burst size or burst epoch.
  - No reference to specific protocols or mission profiles; the model is generic.

---

## Applicability by MAC

- **MacCSMA, MacALOHA, MacCSMA_RTS:** Both profiles are supported. Profile is selected via `**.mac.trafficProfile`; parameters are read from NED/ini as above.
- **MacTDMA:** Traffic profile is not applied. TDMA remains slot-based (one packet per assigned slot). Slot duration is derived from `packetInterval` and `numNodes` as before; profile selection has no effect on TDMA.

---

## Configuration Examples

**Periodic only (low-rate, housekeeping-style):**

```ini
**.mac.trafficProfile = "periodic"
**.mac.packetInterval = 0.1
```

(One packet per node every 0.1 s on average; all values are configurable.)

**Periodic with bursts:**

```ini
**.mac.trafficProfile = "periodicWithBurst"
**.mac.baseInterval = 0.1
**.mac.burstInterval = 2.0
**.mac.burstSize = 8
**.mac.interPacketInBurst = 0.02
```

(Periodic stream every 0.1 s; every 2 s a burst of 8 packets with 0.02 s between packet starts. All values configurable.)

**Selecting a profile in a config:**

Use the pre-defined configs `TrafficProfile-Periodic` and `TrafficProfile-PeriodicWithBurst` in `simulations/omnetpp.ini`, or copy the relevant `**.mac.*` lines into any other config. Override any of the parameters (e.g. `packetInterval`, `burstInterval`, `burstSize`) as needed.

---

## Assumptions (Summary)

- Traffic is generated at the MAC layer as “one packet per generation event”; no payload size or bit-rate modelling.
- For `periodicWithBurst`, periodic and burst streams are independent; both can create packets at the same time.
- Default NED values (e.g. 0.05 s, 1.0 s, 5 packets, 0.01 s) are for simulation only and are not tied to any real system; all must be set via configuration for a given study.
- No performance or reliability claims are made for any profile; they only define when packets are offered to the MAC.
