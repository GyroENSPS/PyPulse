# PyPulse

PyPulse is a Python-based graphical interface for designing, previewing, and streaming
pulse sequences to a **Swabian Instruments PulseStreamer 8/2**.

It allows users to define pulse patterns through an interactive table, declare
user variables with Python expressions, visualize waveforms in real time, and
generate full measurement sequences with sweep parameters and hardware triggers.

PyPulse also exposes a **TCP command server** so it can be controlled remotely
from any Python script or Jupyter notebook.

---

## Features

- Interactive pulse table (digital channels D0–D7, analog A0–A1)
- User variable table with Python expression support and automatic dependency resolution
- Real-time waveform preview (pyqtgraph)
- Full measurement sequence generation with configurable sweep, triggers, and repetitions
- Save/load pulse and variable configurations (`.cfg` files)
- Direct streaming to PulseStreamer 8/2 (infinite loop or N times)
- Hardware configuration via `config/hardware.cfg`
- **TCP API** for remote control from scripts and notebooks

---

## Requirements

- Python 3.10+
- PyCharm (recommended) or any Python IDE
- A Swabian Instruments PulseStreamer 8/2 (optional for UI-only use)

---

## Installation

### 1. Clone the repository

Open PyCharm, go to **File → New Project from Version Control** and enter:

```
https://github.com/GyroENSPS/PyPulse.git
```

Or clone manually in a terminal:

```bash
git clone https://github.com/GyroENSPS/PyPulse.git
cd PyPulse
```

### 2. Create a virtual environment

In PyCharm: **File → Settings → Project: PyPulse → Python Interpreter → Add Interpreter → Virtualenv → New**.

Or in terminal:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure hardware

Edit `config/hardware.cfg` to match your setup:

```ini
[pulse_streamer]
ip    = 169.254.8.2
clock = internal      # "internal" or "external" (10 MHz)
```

### 5. Run

```bash
python main.py
```

Or in PyCharm, right-click `main.py` → **Run 'main'**.

---

## Project Structure

```
PyPulse/
├── main.py                    # Entry point
├── client.py                  # TCP client for remote control
├── config/
│   ├── hardware.cfg           # Hardware configuration
│   ├── pulse_config/          # Saved pulse configurations
│   └── var_config/            # Saved variable configurations
├── gui/
│   ├── main_window.py         # Main window — signal connections
│   ├── pulse_table_widget.py  # Pulse table logic
│   ├── pulse_viewer.py        # Waveform display (pyqtgraph)
│   └── ui_files/              # Auto-generated PyQt5 UI files
├── hardware/
│   ├── pattern.py             # Pattern data structure
│   ├── pulse_streamer.py      # PulseStreamer driver
│   └── sequence_builder.py    # Pattern → Sequence converter
├── logic/
│   ├── sequence_logic.py      # Sequence generation pipeline
│   └── var_logic.py           # Variable table logic
├── sequences/                 # Auto-generated sequence summary files
└── server/
    └── command_server.py      # TCP command server
```

---

## Usage

1. **Define variables** in the variable table (name + Python expression).
   Variables can reference each other — PyPulse resolves dependencies automatically.

2. **Build the pulse table** — each column is a segment, each row a channel.
   Select the duration variable for each segment via the top ComboBox.

3. **Preview the waveform** using the *Plot Pulse* button (Tab 1).

4. **Configure the sweep** (Tab 2): set min/max/step values, number of points,
   triggers per point and per sequence.

5. **Compute the sequence** — click *Compute Sequence* to generate the full pattern.
   A summary file is automatically saved to `sequences/last_measurement_sequence.txt`.

6. **Stream to hardware** — click *Run Continuous* or *Run N times*
   (requires a connected PulseStreamer at the configured IP).

---

## Remote Control API

PyPulse starts a TCP server on `localhost:5025` at launch.
You can control it from any Python script or Jupyter notebook using `client.py`.

### Quick start

```python
import sys
sys.path.insert(0, r"C:\path\to\PyPulse")
from client import PyPulseClient

ps = PyPulseClient()   # host="localhost", port=5025
ps.connect()

print(ps.idn())        # PyPulse,1.0

# Configure sweep
ps.set_min(0)
ps.set_max(2_000_000)
ps.set_num_points(50)
ps.set_n_repeat(10)

# Update a variable expression
ps.set_var("tau", "500000")
ps.set_var("t_pi", "tau / 2")

# Load a saved configuration
ps.load_pulse_config("config/pulse_config/rabi.cfg")
ps.load_var_config("config/var_config/rabi_vars.cfg")

# Compute and stream
ps.compute_sequence()
ps.run_continuous()

# Stop
ps.stop()
ps.disconnect()
```

### Ramsey example (Jupyter notebook)

```python
from client import PyPulseClient
import time

ps = PyPulseClient()
ps.connect()

ps.load_pulse_config("config/pulse_config/ramsey.cfg")
ps.load_var_config("config/var_config/ramsey_vars.cfg")

for tau_ns in range(0, 5_000_000, 100_000):
    ps.set_var("tau", str(tau_ns))
    ps.set_min(tau_ns)
    ps.set_max(tau_ns)
    ps.set_num_points(1)
    ps.compute_sequence()
    ps.run_n_times()
    time.sleep(0.5)

ps.stop()
ps.disconnect()
```

### API command reference

| Command | Client method | Description |
|---|---|---|
| `*IDN?` | `idn()` | Identification string |
| `RUN_CONTINUOUS` | `run_continuous()` | Stream sequence in infinite loop |
| `RUN_N_TIMES` | `run_n_times()` | Stream sequence N times |
| `STOP` | `stop()` | Stop streaming, reset outputs |
| `COMPUTE_SEQUENCE` | `compute_sequence()` | Compute full measurement sequence |
| `SAVE_PULSE_CONFIG` | — | Save current pulse config |
| `LOAD_PULSE_CONFIG <path>` | `load_pulse_config(path)` | Load a pulse `.cfg` file |
| `LOAD_VAR_CONFIG <path>` | `load_var_config(path)` | Load a variable `.cfg` file |
| `SET_VAR <name> <expr>` | `set_var(name, expr)` | Update a variable expression |
| `SET_MIN <val>` | `set_min(val)` | Set sweep minimum (ns) |
| `SET_MAX <val>` | `set_max(val)` | Set sweep maximum (ns) |
| `SET_NUM_POINTS <val>` | `set_num_points(val)` | Set number of sweep points |
| `SET_N_REPEAT <val>` | `set_n_repeat(val)` | Set repetitions per point |
| `GET? min` | `get("min")` | Read current sweep minimum |
| `GET? max` | `get("max")` | Read current sweep maximum |
| `GET? num_points` | `get("num_points")` | Read number of points |
| `GET? n_repeat` | `get("n_repeat")` | Read repetitions per point |
