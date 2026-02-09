# Qualitative Failure Trend Indicators

Post-processing adds **observations** (aggregated metrics from scalar results) and **interpretations** (qualitative trend flags). There is no curve fitting, no extrapolation, and no claim of optimality.

---

## Separation: Observation vs Interpretation

| Layer | Meaning | Example |
|-------|--------|--------|
| **Observation** | Values computed from recorded scalars (sums, max, mean, ratios). Raw or aggregated facts only. | `obs_max_e2e_delay_sec`, `obs_collision_ratio`, `obs_retry_exhaustion_ratio` |
| **Interpretation** | Qualitative labels derived by applying fixed thresholds to observations. Subjective criteria for “high latency”, “collision-dominated”, “retry exhaustion onset”. | `interpret_latency_high`, `interpret_collision_dominated`, `interpret_retry_exhaustion_onset` |

Interpretation is for **trend labeling only**. It does not imply that thresholds are optimal or that regimes are strictly defined.

---

## Observations (Computed from Scalars)

Per experiment (one run), scalars from all MAC modules (nodes) are aggregated:

| Observation | Definition |
|-------------|------------|
| `obs_total_generated` | Sum of `Generated` over all nodes |
| `obs_total_delivered` | Sum of `Delivered` over all nodes |
| `obs_total_collisions` | Sum of `Collisions` over all nodes |
| `obs_total_tx_attempts` | Sum of `TX_Attempts` over all nodes |
| `obs_total_retries_exhausted` | Sum of `RetriesExhausted` over all nodes |
| `obs_max_e2e_delay_sec` | Maximum of `E2EDelayMax` over all nodes (seconds) |
| `obs_mean_pdr` | Mean of `PDR` over all nodes |
| `obs_collision_ratio` | `obs_total_collisions / obs_total_tx_attempts` (undefined if no attempts) |
| `obs_retry_exhaustion_ratio` | `obs_total_retries_exhausted / obs_total_generated` (undefined if no generated) |

No curve fitting or extrapolation is applied to these values.

---

## Trend Indicators (Interpretation)

Thresholds are configurable in `scripts/trend_config.yaml` (or `trend_config_example.yaml`). Defaults are illustrative only.

### 1. Latency high (unbounded trend)

- **Interpretation flag:** `interpret_latency_high` (0 or 1)
- **Rule:** `interpret_latency_high = 1` if `obs_max_e2e_delay_sec > latency_unbounded_threshold_sec`
- **Meaning:** The observed maximum end-to-end delay in this run exceeds the configured threshold. Used as a **qualitative** indicator that latency is high in this regime (e.g. approaching unbounded or unacceptable). Not a proof of unboundedness; threshold is chosen heuristically (e.g. multiple of typical packet interval).

### 2. Collision-dominated regime

- **Interpretation flag:** `interpret_collision_dominated` (0 or 1)
- **Rule:** `interpret_collision_dominated = 1` if `obs_collision_ratio > collision_dominated_ratio_threshold`
- **Meaning:** A large fraction of transmission attempts resulted in collisions. Used to label runs where the regime is **qualitatively** collision-dominated. Threshold is not derived from a model fit.

### 3. Retry exhaustion onset

- **Interpretation flag:** `interpret_retry_exhaustion_onset` (0 or 1)
- **Rule:** `interpret_retry_exhaustion_onset = 1` if `obs_retry_exhaustion_ratio > retry_exhaustion_onset_ratio_threshold`
- **Meaning:** A non-negligible fraction of generated packets hit retry exhaustion. Used to flag **onset** of retry exhaustion as a problem. Threshold is a chosen cutoff, not an optimal or fitted value.

### 4. Any trend

- **Interpretation flag:** `interpret_any_trend` (0 or 1)
- **Rule:** `interpret_any_trend = 1` if any of the above three flags is 1.

---

## Output Files

- **`results/sweep/trends.csv`**  
  One row per experiment. Columns:
  - Manifest: `experiment_id`, `seed`, `num_nodes`, `packet_interval`, `mac`, `network`, `output_dir`
  - Observation: `obs_*`
  - Interpretation: `interpret_*`

The file may start with comment lines that state that `obs_*` are observations and `interpret_*` are qualitative trend indicators (no fitting, no extrapolation, no optimality claim).

---

## Usage

1. Run a sweep (see `SWEEP.md`) so that `results/sweep/` contains a `manifest.csv` and one directory per run with result files (`.sca` or CSV export).
2. If OMNeT++ wrote binary/SQLite `.sca`, you can export scalars to CSV with `opp_scavetool` and place the CSV in each run directory, or rely on the script’s SQLite support.
3. From project root:
   ```bash
   python scripts/postprocess_sweep.py
   ```
   Optional: `python scripts/postprocess_sweep.py results/sweep --trend-config scripts/trend_config.yaml`
4. Open `results/sweep/trends.csv` for analysis. Use observation columns for numeric analysis; use interpretation columns only as qualitative trend labels.

---

## Constraints (What This Does Not Do)

- **No curve fitting:** Observations are direct (or simple) aggregates; no regression or fitted curves.
- **No extrapolation:** Only data from the current run is used; no prediction outside the observed range.
- **No optimality claims:** Thresholds are for labeling trends only; they are not asserted to be optimal or theoretically derived.
