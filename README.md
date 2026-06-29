# LogPlotter

A desktop tool for visualizing Crazyflie log files (CSV format). Load one or more CSV files, select which signals to plot, and view the resulting subplots in a scrollable panel.

## Requirements

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Running

### With uv (recommended)

```sh
uv run logplotter.py
```

### With pip

```sh
pip install -r requirements.txt
python logplotter.py
```

## Usage

1. Click **Add Files…** to load one or more CSV log files.
2. In the **Signal Picker**, check the signals you want to plot.
3. Use **Plot Configuration** to toggle options like linked x-axes, zero-based time, and grid lines.
4. Plots appear in the right panel, one subplot per selected (file, signal) pair.

## CSV Format

LogPlotter expects CSV files with a `Timestamp` (or `timestamp_ms`) column containing millisecond values, followed by signal columns named in `group.signal` format (e.g. `stateEstimate.x`).

Example:
```
Timestamp,stateEstimate.x,stateEstimate.y,stateEstimate.z
119637,0.12,0.05,0.98
119737,0.13,0.05,0.97
```
