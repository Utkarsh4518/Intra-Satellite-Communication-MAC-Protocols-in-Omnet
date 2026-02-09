# Automated Experiment Sweeps

Scripted batch runs over **node count**, **offered load**, and **MAC protocol**. No manual execution; unique experiment IDs; organized output directories. No result analysis (only run generation and organization).

## Directory structure

All sweep outputs go under `results/sweep/` (or a path set in the config):

```
results/
  sweep/
    manifest.csv              # One row per run: experiment_id, seed, num_nodes, packet_interval, mac, network, output_dir, status
    0001_nodes4_load0.05_MacTDMA/
    0002_nodes4_load0.05_MacCSMA/
    0003_nodes4_load0.05_MacALOHA/
    ...
    000N_nodes12_load0.2_MacCSMA_RTS/
```

- **Experiment ID**: Unique integer (1, 2, …) used for seed (`seed = base_seed + experiment_id`) and as prefix in the directory name.
- **Subdir name**: `{experiment_id:04d}_nodes{num_nodes}_load{packet_interval}_{mac}` (e.g. `0001_nodes4_load0.05_MacTDMA`).
- **Manifest**: `manifest.csv` lists every run with parameters and `output_dir` for later analysis.

## Usage

1. **From project root** (required so paths resolve correctly):

   ```bash
   python scripts/run_sweep.py
   ```

   This uses `scripts/sweep_config.yaml` if present, otherwise `scripts/sweep_config_example.yaml`.

2. **Use a specific config file**:

   ```bash
   python scripts/run_sweep.py scripts/my_sweep.yaml
   ```

3. **Dry run** (print planned runs and manifest path, do not execute):

   ```bash
   python scripts/run_sweep.py --dry-run
   ```

## Example sweep configuration

See `scripts/sweep_config_example.yaml`. Copy to `scripts/sweep_config.yaml` and edit.

```yaml
base_seed: 1000
sim_time_limit: 50
network: lifihiddennode.LiFiHiddenRing

node_counts: [4, 8, 12]
offered_loads: [0.05, 0.1, 0.2]   # packetInterval (s); 0.05 => 20 pkts/s per node
mac_protocols: [MacTDMA, MacCSMA, MacALOHA, MacCSMA_RTS]
```

- **base_seed**: Seed for run 1 is `base_seed + 1`, etc.
- **network**: Must match a network in `omnetpp.ini` (e.g. `lifihiddennode.LiFiHiddenRing`). `numNodes` is set per run from `node_counts`.
- **offered_loads**: List of `**.mac.packetInterval` values (seconds between packet generations per node).

Optional overrides (relative to project root):

- `sim_exe`: path to executable (default: `src/LiFiHiddenNode2` or `src/LiFiHiddenNode2.exe` on Windows)
- `ini_file`: path to ini (default: `simulations/omnetpp.ini`)
- `results_root`: root for sweep outputs (default: `results/sweep`)

## Requirements

- Simulation built (e.g. `make` in project root; executable under `src/`).
- Python 3 (no extra deps required; optional `PyYAML` for full YAML parsing; script has a minimal parser if PyYAML is missing).
- Run from **project root** so `-f` and `-n` paths and (if supported) `**.result-dir` resolve correctly.

## Output location

The script passes `--**.result-dir=<output_dir>` so OMNeT++ writes result files (e.g. `.sca`, `.vec`) into the experiment subdir. If your OMNeT++ version does not support that, it may write to the current working directory (project root); in that case you can move or copy `*.sca`, `*.vec` into the corresponding `results/sweep/<exp_dir>/` using the paths in `manifest.csv`.

## Post-processing (trend indicators)

After a sweep, run **post-processing** to get qualitative failure trends (observations + interpretation flags). No curve fitting, no extrapolation, no optimality claims. See **`TREND_INDICATORS.md`** and run from project root:

```bash
python scripts/postprocess_sweep.py
```

This reads `results/sweep/manifest.csv` and each run’s result files, then writes **`results/sweep/trends.csv`** with observation columns (`obs_*`) and interpretation columns (`interpret_*`). Trend thresholds are set in `scripts/trend_config.yaml` (or `trend_config_example.yaml`).
