"""Signal picker: tree widget with File → Group → Signal checkboxes."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SignalPicker(QWidget):
    selection_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("Signals")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._tree)

    def add_file(self, path: str, display_name: str, signals: list[str]):
        """Add a file node with its grouped signals. All start unchecked."""
        file_item = self._make_checkable_item(display_name)
        file_item.setData(0, Qt.ItemDataRole.UserRole, path)

        # Group signals by prefix before the first '.'
        groups: dict[str, list[str]] = {}
        for sig in signals:
            group = sig.split(".")[0] if "." in sig else "(ungrouped)"
            groups.setdefault(group, []).append(sig)

        for group_name, group_sigs in groups.items():
            group_item = self._make_checkable_item(group_name)
            file_item.addChild(group_item)

            for sig in group_sigs:
                sig_item = self._make_checkable_item(sig)
                sig_item.setData(0, Qt.ItemDataRole.UserRole, (path, sig))
                group_item.addChild(sig_item)

            group_item.setExpanded(True)

        file_item.setExpanded(True)
        self._tree.addTopLevelItem(file_item)

    @staticmethod
    def _make_checkable_item(label: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Unchecked)
        return item

    def remove_file(self, path: str):
        """Remove the top-level item corresponding to the given file path."""
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == path:
                self._updating = True
                self._tree.takeTopLevelItem(i)
                self._updating = False
                return

    def clear(self):
        self._updating = True
        self._tree.clear()
        self._updating = False

    # ------------------------------------------------------------------ #
    # Internal checkbox logic
    # ------------------------------------------------------------------ #

    def _on_item_changed(self, item: QTreeWidgetItem, _column: int):
        if self._updating:
            return
        self._updating = True
        try:
            state = item.checkState(0)
            # Cascade to children (but not when we're setting partial state)
            if state != Qt.CheckState.PartiallyChecked:
                self._cascade(item, state)
            # Update all ancestors
            parent = item.parent()
            while parent is not None:
                self._sync_parent(parent)
                parent = parent.parent()
        finally:
            self._updating = False
        self.selection_changed.emit()

    def _cascade(self, item: QTreeWidgetItem, state: Qt.CheckState):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._cascade(child, state)

    def _sync_parent(self, item: QTreeWidgetItem):
        n = item.childCount()
        checked = sum(
            1 for i in range(n)
            if item.child(i).checkState(0) == Qt.CheckState.Checked
        )
        partial = sum(
            1 for i in range(n)
            if item.child(i).checkState(0) == Qt.CheckState.PartiallyChecked
        )
        if checked == n:
            item.setCheckState(0, Qt.CheckState.Checked)
        elif checked == 0 and partial == 0:
            item.setCheckState(0, Qt.CheckState.Unchecked)
        else:
            item.setCheckState(0, Qt.CheckState.PartiallyChecked)

    # ------------------------------------------------------------------ #
    # Query
    # ------------------------------------------------------------------ #

    def get_selected(self) -> list[tuple[str, str]]:
        """Return checked (path, signal) pairs in tree display order."""
        result = []
        for i in range(self._tree.topLevelItemCount()):
            file_item = self._tree.topLevelItem(i)
            for j in range(file_item.childCount()):
                group_item = file_item.child(j)
                for k in range(group_item.childCount()):
                    sig_item = group_item.child(k)
                    if sig_item.checkState(0) == Qt.CheckState.Checked:
                        result.append(sig_item.data(0, Qt.ItemDataRole.UserRole))
        return result
