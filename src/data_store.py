"""Manages loaded CSV file data."""
from collections import OrderedDict
from pathlib import Path

import pandas as pd

_TIMESTAMP_COLS = ("Timestamp", "timestamp_ms")
_BLOCK_COL = "block"


class DataStore:
    def __init__(self):
        self._files: OrderedDict = OrderedDict()  # path -> dict

    def add_file(self, path: str) -> tuple[str, list[str]]:
        """Load a CSV file. Returns (display_name, signal_names).

        Raises ValueError with a user-facing message on format errors.
        Silently returns existing data if path is already loaded.
        """
        if path in self._files:
            info = self._files[path]
            return info["display_name"], info["signals"]

        df = pd.read_csv(path)

        ts_col = next((c for c in _TIMESTAMP_COLS if c in df.columns), None)
        if ts_col is None:
            raise ValueError(
                f"'{Path(path).name}' has no recognized timestamp column.\n"
                "Expected 'Timestamp' or 'timestamp_ms'."
            )

        try:
            df["time_s"] = pd.to_numeric(df[ts_col], errors="raise") / 1000.0
        except (ValueError, TypeError):
            raise ValueError(
                f"'{Path(path).name}': timestamp values are not numeric."
            )

        drop_cols = [ts_col]
        if _BLOCK_COL in df.columns:
            drop_cols.append(_BLOCK_COL)
        df = df.drop(columns=drop_cols)

        signals = [c for c in df.columns if c != "time_s"]
        display_name = self._unique_display_name(Path(path).name)
        self._files[path] = {"display_name": display_name, "df": df, "signals": signals}
        return display_name, signals

    def _unique_display_name(self, basename: str) -> str:
        existing = {info["display_name"] for info in self._files.values()}
        if basename not in existing:
            return basename
        counter = 2
        while f"{basename} ({counter})" in existing:
            counter += 1
        return f"{basename} ({counter})"

    def remove_file(self, path: str):
        self._files.pop(path, None)

    def remove_all(self):
        self._files.clear()

    def get_df(self, path: str) -> pd.DataFrame:
        return self._files[path]["df"]

    def get_display_name(self, path: str) -> str:
        return self._files[path]["display_name"]

    def get_signals(self, path: str) -> list[str]:
        return self._files[path]["signals"]

    def get_paths_in_order(self) -> list[str]:
        return list(self._files.keys())

    def get_global_min_time(self) -> float:
        if not self._files:
            return 0.0
        return min(info["df"]["time_s"].min() for info in self._files.values())

    def is_loaded(self, path: str) -> bool:
        return path in self._files
