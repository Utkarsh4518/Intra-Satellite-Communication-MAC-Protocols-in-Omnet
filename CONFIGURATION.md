# Experiment Configuration Layer

All experiment parameters are defined in a single configuration layer: **`simulations/omnetpp.ini`**. NED files declare parameters with defaults; the ini file overrides them so that no experiment values are hardcoded in C++.

## File-Level Changes

| File | Change |
|------|--------|
| **src/mac/MacInterface.ned** | Added `packetInterval` (double, default 0.05). Commented. |
| **src/mac/MacModules.ned** | MacCSMA: added `deferMax`, `hopDelayMax`. MacALOHA: added `retxMean`, `hopDelayMax`. MacCSMA_RTS: added `rtsHopDelay`. All commented. |
| **src/mac/MacCSMA.cc** | Replaced hardcoded 0.05, 0.03, 0.02 with `par("packetInterval")`, `par("deferMax")`, `par("hopDelayMax")`. |
| **src/mac/MacTDMA.cc** | Replaced hardcoded 20.0 with `par("packetInterval")` for slot time computation (`slotTime = packetInterval / numNodes`). |
| **src/mac/MacALOHA.cc** | Replaced 0.05, 0.02 with `par("packetInterval")`, `par("hopDelayMax")`; 0.05 in exponential with `par("retxMean")`. |
| **src/mac/MacCSMA_RTS.cc** | Replaced 0.05, 0.01 with `par("packetInterval")`, `par("rtsHopDelay")`. |
| **simulations/omnetpp.ini** | Added header block documenting the configuration layer. Added commented entries for node count, topology, seed-set, MAC selection, packetInterval, and MAC-specific parameters. All configs inherit from [General]; config-specific sections override as before. |

No changes to: Node.ned, network NEDs (Ring/Star/Bus), OpticalChannel, MacBase. Simulation behavior is unchanged; only the source of parameter values (ini/NED instead of C++ literals) changed.

## Example Configuration Entries

**Node count (per network):**
```ini
lifihiddennode.LiFiHiddenRing.numNodes = 8
lifihiddennode.LiFiHiddenStar.numNodes = 8
lifihiddennode.LiFiHiddenBus.numNodes = 8
```

**Topology type (choice of network implies numHops: Ring=2, Star/Bus=1):**
```ini
network = lifihiddennode.LiFiHiddenRing
# network = lifihiddennode.LiFiHiddenStar
# network = lifihiddennode.LiFiHiddenBus
```

**Offered traffic load (same for all MACs):**
```ini
**.mac.packetInterval = 0.05
```
(0.05 s between packet generations per node ⇒ 20 packets/s per node.)

**MAC protocol selection:**
```ini
**.macType = "MacTDMA"
# **.macType = "MacCSMA"
# **.macType = "MacALOHA"
# **.macType = "MacCSMA_RTS"
```

**Random seed (reproducibility):**
```ini
seed-set = 0
```

**CSMA-only (when MacCSMA is used):**
```ini
**.mac.maxRetries = 4
**.mac.initialBackoff = 0.01
**.mac.maxBackoff = 0.5
**.mac.deferMax = 0.03
**.mac.hopDelayMax = 0.02
```

**ALOHA-only:**
```ini
**.mac.retxMean = 0.05
**.mac.hopDelayMax = 0.02
```

**CSMA_RTS-only:**
```ini
**.mac.rtsHopDelay = 0.01
```

## How Parameters Propagate Through the Simulation

1. **omnetpp.ini**  
   - Read at startup. `[General]` and the selected `[Config ...]` are merged (config overrides General).  
   - Keys like `**.macType`, `**.mac.packetInterval`, `lifihiddennode.LiFiHiddenRing.numNodes` assign values to module parameters by path.

2. **Network (NED)**  
   - `network = lifihiddennode.LiFiHiddenRing` instantiates that network.  
   - The network’s `numNodes` and `numHops` are set from ini (e.g. `lifihiddennode.LiFiHiddenRing.numNodes = 8`).  
   - The network creates `node[numNodes]` and sets `node[*].numNodes = numNodes`, `node[*].numHops = numHops`.

3. **Node (NED)**  
   - Each node gets `numNodes`, `numHops`, and `macType` from ini or parent.  
   - Node creates submodule `mac: <macType> like MacInterface` and passes `numNodes`, `numHops`.  
   - Parameters under `**.mac.*` in ini (e.g. `**.mac.packetInterval`) apply to every node’s `mac` submodule.

4. **MAC (C++)**  
   - In `initialize()` and `handleMessage()`, MAC code uses `par("packetInterval")`, `par("numNodes")`, `par("numHops")`, and protocol-specific names (`deferMax`, `hopDelayMax`, `retxMean`, `rtsHopDelay`, etc.).  
   - Values come from NED defaults (MacInterface / MacModules) or from ini overrides.  
   - No hardcoded experiment values remain in the MAC .cc files.

5. **Random seed**  
   - `seed-set` in ini is used by the OMNeT++ RNG. All `uniform()`, `exponential()`, etc. are driven by this seed when set, giving reproducible runs.

Result: **Node count**, **topology type** (network + numHops), **offered load** (packetInterval), **MAC protocol** (macType), and **random seed** (seed-set) are all controlled from the ini file; behavior is unchanged from the previous hardcoded setup.
