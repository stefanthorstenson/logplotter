"""Main application window."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSplitter

from data_store import DataStore
from file_picker import FilePicker
from plot_area import PlotArea
from plot_config import PlotConfig
from signal_picker import SignalPicker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogPlotter")
        self.resize(1200, 800)

        self._data_store = DataStore()

        # ── Left panel: three stacked resizable subframes ──────────────────
        left_splitter = QSplitter(Qt.Orientation.Vertical)

        self._file_picker = FilePicker()
        self._signal_picker = SignalPicker()
        self._plot_config = PlotConfig()

        left_splitter.addWidget(self._file_picker)
        left_splitter.addWidget(self._signal_picker)
        left_splitter.addWidget(self._plot_config)
        left_splitter.setSizes([140, 460, 120])

        # ── Right panel ─────────────────────────────────────────────────────
        self._plot_area = PlotArea()

        # ── Main horizontal splitter ────────────────────────────────────────
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self._plot_area)
        main_splitter.setSizes([280, 920])
        self.setCentralWidget(main_splitter)

        # ── Wire up signals ─────────────────────────────────────────────────
        self._file_picker.files_added.connect(self._on_files_added)
        self._file_picker.file_removed.connect(self._on_file_removed)
        self._file_picker.files_cleared.connect(self._on_files_cleared)
        self._signal_picker.selection_changed.connect(self._rerender)
        self._plot_config.config_changed.connect(self._rerender)

    # ── Handlers ────────────────────────────────────────────────────────────

    def _on_files_added(self, paths: list[str]):
        for path in paths:
            try:
                display_name, signals = self._data_store.add_file(path)
            except ValueError as exc:
                QMessageBox.warning(self, "File Load Error", str(exc))
                continue
            self._file_picker.add_file(path, display_name)
            self._signal_picker.add_file(path, display_name, signals)
        self._rerender()

    def _on_file_removed(self, path: str):
        self._data_store.remove_file(path)
        self._signal_picker.remove_file(path)
        self._rerender()

    def _on_files_cleared(self):
        self._data_store.remove_all()
        self._signal_picker.clear()
        self._rerender()

    def _rerender(self):
        self._plot_area.render(
            self._signal_picker.get_selected(),
            self._data_store,
            self._plot_config.start_from_zero,
            self._plot_config.link_x_axes,
            self._plot_config.grid,
        )
