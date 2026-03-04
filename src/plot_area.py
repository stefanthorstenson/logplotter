"""Scrollable plot area: one matplotlib subplot per (file, signal) pair."""
import matplotlib
matplotlib.use("QtAgg")  # must be set before importing backends

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

_SUBPLOT_HEIGHT_PX = 260   # pixels per subplot
_SUBPLOT_HEIGHT_IN = 2.6   # inches per subplot (at 100 DPI)
_DPI = 100


class PlotArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._toolbar: NavigationToolbar2QT | None = None

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._layout.addWidget(self._scroll)

        self._show_empty()

    def _show_empty(self):
        self._remove_toolbar()
        lbl = QLabel("No signals selected")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidget(lbl)

    def _remove_toolbar(self):
        if self._toolbar is not None:
            self._layout.removeWidget(self._toolbar)
            self._toolbar.deleteLater()
            self._toolbar = None

    def render(
        self,
        selected: list[tuple[str, str]],
        data_store,
        start_from_zero: bool,
        link_x_axes: bool,
        grid: bool,
    ):
        if not selected:
            self._show_empty()
            return

        n = len(selected)
        global_min = data_store.get_global_min_time() if start_from_zero else 0.0

        fig = Figure(figsize=(8, _SUBPLOT_HEIGHT_IN * n), dpi=_DPI)
        fig.subplots_adjust(hspace=0.6)

        axes = []
        for idx, (path, signal) in enumerate(selected):
            sharex = axes[0] if (idx > 0 and link_x_axes) else None
            ax = fig.add_subplot(n, 1, idx + 1, sharex=sharex)
            axes.append(ax)

            df = data_store.get_df(path)
            display_name = data_store.get_display_name(path)

            if signal in df.columns:
                col = df[["time_s", signal]].dropna(subset=[signal])
                if not col.empty:
                    ax.plot(col["time_s"] - global_min, col[signal], linewidth=0.8)

            ax.set_title(f"{display_name}:{signal}", fontsize=8, pad=3)
            ax.set_xlabel("Time (s)", fontsize=7)
            ax.set_ylabel(signal, fontsize=7)
            ax.tick_params(labelsize=7)
            ax.grid(grid)

        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(_SUBPLOT_HEIGHT_PX * n)

        # Replace toolbar (above scroll area)
        self._remove_toolbar()
        self._toolbar = NavigationToolbar2QT(canvas, self)
        self._layout.insertWidget(0, self._toolbar)

        self._scroll.setWidget(canvas)
