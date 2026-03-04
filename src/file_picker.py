"""File picker widget: add/clear CSV files."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FilePicker(QWidget):
    files_added = Signal(list)   # list[str] of new file paths
    file_removed = Signal(str)   # single file path
    files_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("Files")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("Add Files…")
        self._remove_btn = QPushButton("Remove File")
        self._clear_btn = QPushButton("Clear All")
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._remove_btn)
        btn_row.addWidget(self._clear_btn)
        layout.addLayout(btn_row)

        self._list = QListWidget()
        layout.addWidget(self._list)

        self._loaded: set[str] = set()
        self._last_dir = ""

        self._add_btn.clicked.connect(self._on_add)
        self._remove_btn.clicked.connect(self._on_remove)
        self._clear_btn.clicked.connect(self._on_clear)

    def _on_add(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select CSV Files", self._last_dir, "CSV Files (*.csv)"
        )
        if not paths:
            return
        self._last_dir = str(Path(paths[0]).parent)
        new_paths = [p for p in paths if p not in self._loaded]
        if new_paths:
            self.files_added.emit(new_paths)

    def _on_remove(self):
        row = self._list.currentRow()
        if row < 0:
            return
        item = self._list.takeItem(row)
        path = item.data(Qt.ItemDataRole.UserRole)
        self._loaded.discard(path)
        self.file_removed.emit(path)

    def _on_clear(self):
        self._list.clear()
        self._loaded.clear()
        self.files_cleared.emit()

    # Called by MainWindow after a file is successfully loaded.
    def add_file(self, path: str, display_name: str):
        self._loaded.add(path)
        item = QListWidgetItem(display_name)
        item.setToolTip(path)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self._list.addItem(item)

    def clear(self):
        self._list.clear()
        self._loaded.clear()
