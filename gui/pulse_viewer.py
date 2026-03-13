import numpy as np
import pyqtgraph
from PyQt5.QtGui import QColor

CHANNEL_COLORS = [
                    "#1f77b4",  # bleu
                    "#ff7f0e",  # orange
                    "#2ca02c",  # vert
                    "#d62728",  # rouge
                    "#9467bd",  # violet
                    "#8c564b",  # brun
                    "#e377c2",  # rose
                    "#7f7f7f",  # gris
                    "#bcbd22",  # jaune-vert
                    "#17becf"   # cyan
                    ]
CHANNEL_LABELS = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "A0", "A1"]
PLOT_OFFSET = -2.1


class PulseViewer:

    def __init__(self, plot_widget):
        """plot_widget : the pyqtgraph PlotWidget from the UI (self.ui.pulse_view)."""
        self.plot = plot_widget

    def plot_pattern(self, pulse_durations: np.ndarray, IO_matrix: np.ndarray,
                     variable_index: list, min_val: float = 0, max_val: float = 0):
        """
        Plots all 10 channels stacked vertically.
        Highlights the sweep variable region if variable_index is not empty.
        """
        self.plot.clear()

        # Compute time axis (oversampled for step plot)
        pulses_timings = [sum(pulse_durations[:i // 2]) for i in range(len(pulse_durations) * 2 + 1)]

        # Highlight variable region
        begin_lengths = np.copy(pulse_durations)
        end_lengths   = np.copy(pulse_durations)
        for var_col in variable_index:
            begin_lengths[var_col] = min_val
            t_start = sum(begin_lengths[:var_col + 1])
            end_lengths[var_col]   = max_val
            t_end   = t_start + (max_val - min_val)
            region = pyqtgraph.LinearRegionItem(
                values=(t_start, t_end),
                orientation=pyqtgraph.LinearRegionItem.Vertical
            )
            region.setBrush(pyqtgraph.mkBrush("turquoise"))
            region.setOpacity(0.2)
            region.setZValue(-10)
            region.setMovable(False)
            self.plot.addItem(region)
            begin_lengths = np.copy(pulse_durations)
            end_lengths   = np.copy(pulse_durations)

        # Draw vertical dashed separators
        for x in pulses_timings:
            line = pyqtgraph.InfiniteLine(
                pos=x, angle=90,
                pen=pyqtgraph.mkPen(color=(0, 0, 0, 50), width=0.5,
                                    style=pyqtgraph.QtCore.Qt.DashLine)
            )
            self.plot.addItem(line)

        # Plot each channel
        for i in range(len(IO_matrix)):
            offset = i * PLOT_OFFSET
            io_vals = IO_matrix[i]
            io_plot = [io_vals[j // 2] + offset for j in range(len(io_vals) * 2)]
            io_plot.append(io_plot[-1])
            io_plot = io_plot[-1:] + io_plot[:-1]  # rotate by -1

            fill_color = QColor(CHANNEL_COLORS[i])
            fill_color.setAlphaF(0.5)

            self.plot.plot(
                pulses_timings, io_plot,
                pen=pyqtgraph.mkPen(color=CHANNEL_COLORS[i], width=2),
                brush=fill_color,
                fillLevel=offset
            )

    def clear(self):
        self.plot.clear()
