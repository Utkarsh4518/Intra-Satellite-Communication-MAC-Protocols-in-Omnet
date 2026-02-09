# Rule-Based MAC Selection Helper

Deterministic, rule-based MAC selection. Not an optimizer; no machine learning. Each decision returns the exact reason string for the matching rule.

See **README.md** for CLI usage and disclaimer.

---

## Rule table

| # | Condition | Output | Reason (short) |
|---|-----------|--------|----------------|
| 1 | latency_sensitivity == "high" | MacTDMA | Latency critical -> bounded delay |
| 2 | offered_load == "high" | MacTDMA | High load -> avoid contention |
| 3 | node_count >= 9 | MacTDMA | Many nodes -> contention-based MACs degrade |
| 4 | latency_sensitivity == "low" AND node_count <= 4 AND offered_load == "low" | MacCSMA | Low contention, relaxed latency |
| 5 | latency_sensitivity == "low" AND node_count <= 8 AND offered_load == "low or medium" | MacCSMA_RTS | Moderate contention, hidden-node |
| 6 | default | MacTDMA | Default to deterministic MAC |

Evaluation order: first match wins.

---

## Inputs

- **latency_sensitivity:** `"high"` \| `"low"`
- **node_count:** integer
- **offered_load:** `"low"` \| `"medium"` \| `"high"` **or** numeric packet interval in seconds (float).  
  Numeric mapping: `>= 0.1` → low, `>= 0.05` → medium, `< 0.05` → high.

---

## Validation examples

| latency_sensitivity | node_count | offered_load | Preferred MAC | Reason |
|--------------------|------------|--------------|---------------|--------|
| high | 4 | 0.1 | MacTDMA | Latency critical |
| low | 4 | low | MacCSMA | Low contention |
| low | 8 | 0.05 | MacCSMA_RTS | Moderate contention |
| low | 12 | low | MacTDMA | Many nodes |
| low | 6 | 0.02 | MacTDMA | High load |
