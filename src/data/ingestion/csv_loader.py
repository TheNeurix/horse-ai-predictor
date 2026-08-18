"""CSV loading helpers for local racing data ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.data.ingestion.base import RacingDataSource


class CSVLoaderError(ValueError):
    """Raised when a CSV file cannot be loaded safely."""


class CSVFileNotFoundError(FileNotFoundError, CSVLoaderError):
    """Raised when a requested CSV file path does not exist."""


class CSVMalformedError(CSVLoaderError):
    """Raised when pandas cannot parse a CSV file."""


def load_csv_file(path: str | Path, **read_csv_kwargs: object) -> pd.DataFrame:
    """Load a CSV file into a DataFrame with predictable error handling."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise CSVFileNotFoundError(f"CSV file does not exist: {csv_path}")
    if not csv_path.is_file():
        raise CSVLoaderError(f"CSV path is not a file: {csv_path}")

    options: dict[str, object] = {"on_bad_lines": "error"}
    options.update(read_csv_kwargs)

    try:
        return pd.read_csv(csv_path, **options)
    except pd.errors.EmptyDataError as exc:
        raise CSVMalformedError(f"CSV file is empty: {csv_path}") from exc
    except pd.errors.ParserError as exc:
        raise CSVMalformedError(f"Malformed CSV file: {csv_path}") from exc
    except UnicodeDecodeError as exc:
        raise CSVMalformedError(
            f"CSV file could not be decoded as text: {csv_path}"
        ) from exc
    except OSError as exc:
        raise CSVLoaderError(f"Could not read CSV file: {csv_path}") from exc


@dataclass(frozen=True)
class LocalCSVRacingDataSource(RacingDataSource):
    """Minimal local-file implementation of the data-source contract."""

    race_data_path: str | Path
    performance_data_path: str | Path
    trackwork_data_path: str | Path | None = None
    odds_data_path: str | Path | None = None
    name: str = "local-csv"

    @property
    def source_name(self) -> str:
        return self.name

    def load_race_data(self) -> pd.DataFrame:
        return load_csv_file(self.race_data_path)

    def load_performance_data(self) -> pd.DataFrame:
        return load_csv_file(self.performance_data_path)

    def load_trackwork_data(self) -> pd.DataFrame | None:
        if self.trackwork_data_path is None:
            return None
        return load_csv_file(self.trackwork_data_path)

    def load_odds_data(self) -> pd.DataFrame | None:
        if self.odds_data_path is None:
            return None
        return load_csv_file(self.odds_data_path)
