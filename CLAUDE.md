# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

PyPulse is a PyQt5 desktop GUI for designing pulse sequences and streaming them to a **Swabian Instruments PulseStreamer 8/2**. It also exposes a TCP command server (localhost:5025) for remote control from scripts or Jupyter notebooks.

## Commands

**Run the application:**
```bash
python main.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Regenerate UI Python files after editing a `.ui` file in Qt Designer:**
```bash
python gui/reload_UI.py
```
This runs `pyuic5` and also patches the `resources_rc` import to the correct package path (`gui.ui_files.py_files`).

**Regenerate Qt resources (icons etc.) after editing `resources.qrc`:**
```bash
cd gui/ui_files && pyrcc5 resources.qrc -o py_files/resources_rc.py
```

## Architecture

### Startup flow
`main.py` creates the `QApplication`, instantiates `MainWindow`, then starts `CommandServer` in a daemon thread before entering the Qt event loop.

### Component map

| Module | Role |
|---|---|
| `gui/main_window.py` | Orchestrates all subsystems; owns all signal→slot connections; runs sequence computation in a background `SequenceWorker(QThread)` to avoid blocking the UI; updates `label_sequence_duration` with the formatted total duration after each successful compute |
| `gui/pulse_table_widget.py` | Manages the pulse table widget — row 0 = `QComboBox` (duration variable selector), rows 1–8 = `QCheckBox` (digital channels D0–D7), rows 9–10 = `QTableWidgetItem` float (analog A0–A1) |
| `gui/pulse_viewer.py` | pyqtgraph waveform display; called for both the single-pattern preview and the sequence preview |
| `logic/var_logic.py` | Manages the variable table; evaluates Python expressions with iterative dependency resolution (bubbles unresolvable rows downward); syncs variable names into all pulse-table ComboBoxes |
| `logic/sequence_logic.py` | Core computation: reads both tables, sweeps a variable over `num_points`, builds `final_patterns` in one of two trigger modes (overlap or insert), exports `.txt` summary |
| `hardware/pulse_streamer.py` | Thin wrapper around the `pulsestreamer` SDK (`PulseStreamer`, `Sequence`, `ClockSource`) |
| `hardware/sequence_builder.py` | Converts `final_patterns` (list of 10 lists of `(duration, value)` tuples) into a `Sequence` object ready to stream |
| `hardware/pattern.py` | Intermediate data structure used by `SequenceBuilder` |
| `server/command_server.py` | TCP server (localhost:5025); runs in a daemon thread; uses a `pyqtSignal` to marshal commands back to the Qt main thread for safe UI access |
| `client_PyPulse.py` | TCP client — import and use from external scripts or notebooks |
| `sequences/base_sequence.py` | Abstract base class for programmatic sequences (not part of the GUI pipeline) |

### Data flow for a measurement sequence

```
VarLogic (var table)  ──┐
                         ├──▶ SequenceLogic.build_measurement_sequence()
PulseTableWidget         │        └─▶ final_patterns: list[10 × list[(duration_ns, value)]]
(pulse table)    ────────┘
                                            │
                                            ▼
                              SequenceBuilder.build()
                                            │
                                            ▼
                              PulseStreamerDriver.stream_*(sequence)
```

`final_patterns` always has 10 elements (indices 0–7 digital, 8–9 analog); unused channels are `None`.

### Two point-trigger modes (in `build_measurement_sequence`)
- **Overlap** (`insert_point_trigger=False`): the trigger pulse overlaps the measurement pattern on its own dedicated channel.
- **Insert** (`insert_point_trigger=True`): a silent slot (all channels 0) of `point_trigger_duration` ns is prepended before each measurement point; other channels are off during this slot.

### Variable expression evaluation
Variable cells contain arbitrary Python expressions that may reference earlier variables. `VarLogic.create_python_var()` resolves them with an iterative `exec` loop (up to 100 retries). `sort_and_resolve()` also physically reorders table rows to bubble dependent variables downward. All durations are in **nanoseconds**.

### TCP server / client protocol
Commands are SCPI-like plain-text strings over TCP. The server dispatches via `pyqtSignal` to ensure all Qt widget access happens on the main thread. See the full command table in `README.md` or `server/command_server.py._dispatch()`.

## Configuration files

- `config/hardware.cfg` — PulseStreamer IP and clock source (`internal` / `external`).
- `config/pulse_config/*.cfg` — Saved pulse table states (ConfigParser format, sections = row labels, keys = column indices).
- `config/var_config/*.cfg` — Saved variable table states (sections = column headers, keys = row indices).
- Default configs loaded on startup: `config/pulse_config/default_pulse.cfg` and `config/var_config/default_var_config.cfg`.

## UI files

The `.ui` files in `gui/ui_files/` are edited in Qt Designer. The generated Python files live in `gui/ui_files/py_files/` and are **not** manually edited. Always regenerate with `reload_UI.py` after any `.ui` change.