# PyPulse

PyPulse is a Python-based graphical interface for designing, previewing, and streaming
pulse sequences to a **Swabian Instruments PulseStreamer 8/2**.

It allows users to define pulse patterns through an interactive table, declare
user variables with Python expressions, visualize waveforms in real time, and
generate full measurement sequences with sweep parameters and hardware triggers.

---

## Features

- Interactive pulse table (digital channels D0–D7, analog A0–A1)
- User variable table with Python expression support and automatic dependency resolution
- Real-time waveform preview (pyqtgraph)
- Full measurement sequence generation with configurable sweep, triggers, and repetitions
- Save/load pulse and variable configurations (`.cfg` files)
- Direct streaming to PulseStreamer 8/2 (infinite loop or N times)
- Hardware configuration via `config/hardware.cfg`

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
ip    = 169.254.8.2   # IP address of your PulseStreamer
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
├── config/
│   ├── hardware.cfg           # Hardware configuration
│   ├── pulse_config/          # Saved pulse configurations
│   └── var_config/            # Saved variable configurations
├── gui/
│   ├── main_window.py         # Main window — signal connections
│   ├── pulse_table_widget.py  # Pulse table logic
│   ├── pulse_viewer.py        # Waveform display (pyqtgraph)
│   └── ui_files/              # Auto-generated PyQt5 UI files
├── logic/
│   ├── sequence_logic.py      # Sequence generation pipeline
│   └── var_logic.py           # Variable table logic
└── hardware/
    ├── pattern.py             # Pattern data structure
    ├── pulse_streamer.py      # PulseStreamer driver
    └── sequence_builder.py    # Pattern → Sequence converter
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

6. **Stream to hardware** — click *Run Continuous* or *Run N times*
   (requires a connected PulseStreamer at the configured IP).
