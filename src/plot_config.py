"""Plot configuration widget."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget


class PlotConfig(QWidget):
    config_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("Plot Config")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        self._zero_cb = QCheckBox("Start time from zero")
        self._link_cb = QCheckBox("Link X axes")
        self._grid_cb = QCheckBox("Grid")
        for cb in (self._zero_cb, self._link_cb, self._grid_cb):
            cb.setChecked(True)
            layout.addWidget(cb)
        layout.addStretch()

        self._zero_cb.toggled.connect(self.config_changed)
        self._link_cb.toggled.connect(self.config_changed)
        self._grid_cb.toggled.connect(self.config_changed)

    @property
    def start_from_zero(self) -> bool:
        return self._zero_cb.isChecked()

    @property
    def link_x_axes(self) -> bool:
        return self._link_cb.isChecked()

    @property
    def grid(self) -> bool:
        return self._grid_cb.isChecked()
