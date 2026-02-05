# Topology vs MAC performance in intra-satellite optical networks

## Goal

Understand whether **MAC protocol conclusions are topology-dependent or architecture-agnostic**: do TDMA, CSMA, and ALOHA keep the same relative ranking when we switch from **star** (1 hop) to **ring** (multi-hop)?

## Topologies and hop count

| Topology | numHops | Interpretation |
|--------|---------|----------------|
| **Star** | 1 | Node–hub: one transmission = one logical delivery. |
| **Ring** | 2 | Typical path along ring: two channel acquisitions per logical packet (two hops). |
| **Bus** | 1 | Single shared medium, same as star for hop count. |

- **Star** and **Bus** use `numHops = 1`: each successful transmission counts as one delivered packet.
- **Ring** uses `numHops = 2`: each logical packet requires **two** successful transmissions (two hops) before it is counted as delivered.

So the same MAC and same per-node **logical** load (e.g. 20 packets/s) produce **more channel load** on the ring, because every packet uses the channel twice.

## How hop count affects metrics

### Transmission attempts

- **Star (1 hop):** One success ⇒ one delivery ⇒ **AvgTxAttemptsPerDelivery ≈ 1** (plus retries on collision).
- **Ring (2 hops):** Two successes ⇒ one delivery ⇒ **AvgTxAttemptsPerDelivery ≈ 2** in the absence of collisions; with retries it will be ≥ 2.

So **transmission attempts scale with hop count**. The scalar **AvgTxAttemptsPerDelivery** in the results reflects this (and will be close to `numHops` when collisions are low).

### Delay

- **Star:** E2E delay = time from packet generation to the single successful transmission.
- **Ring:** E2E delay = time from packet generation to the **second** successful transmission (both hops must succeed).

So **delay increases with hop count**: more channel acquisitions and more contention per logical packet. **E2EDelayMean**, **E2EDelayMax**, and **E2EDelayJitter** all capture this.

### Contention and PDR

- On the **ring**, the same logical packet rate per node implies **about twice the channel traffic** (2 hops per packet). So:
  - Collision probability goes up.
  - **PDR** can drop more on the ring than on the star for contention-based MACs (CSMA, ALOHA).
  - **RetriesExhausted** (CSMA) can increase on the ring.

So **hop count amplifies contention**: conclusions that hold for star may change for ring when we compare MACs.

## Do MAC rankings change with topology?

- **TDMA:** No contention; each node has fixed slots. Doubling the number of channel uses per packet (ring) mainly **scales delay and attempts by 2**; PDR stays 1. So **TDMA remains best** for PDR and predictability in both topologies.
- **CSMA / ALOHA:** On the ring, more attempts per packet and higher load → more collisions and retries → **PDR can drop and delay/jitter can grow** compared to star. So:
  - **Ranking by PDR:** TDMA > CSMA > ALOHA typically holds in both topologies, but the **gap** between contention-based and TDMA can **widen on the ring**.
  - **Ranking by delay/jitter:** TDMA stays best; CSMA and ALOHA get worse on the ring, so the conclusion that “TDMA is better for predictability” becomes **stronger**, not weaker.

So:

- **Conclusions are not reversed by topology**: TDMA remains the most robust and predictable.
- **Conclusions are topology-dependent in magnitude**: contention-based MACs degrade more on the ring (multi-hop) than on the star (single-hop). So MAC choices are **architecture-aware**: for ring-like (multi-hop) intra-satellite optical nets, preferring TDMA (or hybrid) is even more important than in a star.

## How to run the topology experiments

Use the **Topology-*** configs in `simulations/omnetpp.ini`:

- **Topology-Star-TDMA-8**, **Topology-Ring-TDMA-8**
- **Topology-Star-CSMA-8**, **Topology-Ring-CSMA-8**
- **Topology-Star-ALOHA-8**, **Topology-Ring-ALOHA-8**

Same MAC and same node count (8); only network (Star vs Ring) and thus **numHops** (1 vs 2) change.

## What to compare

1. **AvgTxAttemptsPerDelivery**  
   Star ≈ 1 (plus retries); Ring ≈ 2 (plus retries). Confirms that attempts scale with hop count.

2. **PDR**  
   For each MAC, compare Star vs Ring. Expect a larger drop on the ring for CSMA and ALOHA; TDMA stays at 1.

3. **E2EDelayMean / E2EDelayMax / E2EDelayJitter**  
   Higher on the ring for all MACs; contention-based MACs show a bigger increase.

4. **MAC ranking (PDR, then delay/jitter)**  
   Check whether TDMA > CSMA > ALOHA holds in both topologies and whether the **difference** between TDMA and contention-based MACs is larger on the ring.

## Short conclusion

- **Hop count** increases **transmission attempts** and **delay** proportionally and **increases contention** (more channel uses per logical packet).
- **MAC rankings** (TDMA best, then CSMA, then ALOHA) are **topology-consistent**, but **degradation of contention-based MACs is topology-dependent**: it is stronger on the ring. So the takeaway is **architecture-aware**: for multi-hop (ring-like) intra-satellite optical networks, MAC conclusions are not reversed, but the case for TDMA (or TDMA–CSMA hybrid) is **stronger** than in a single-hop star.
