"""Generic local-file data source adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import pandas as pd

from src.data.ingestion.base import RacingDataSource, SourceMetadata
from src.data.ingestion.csv_loader import load_csv_file
from src.data.ingestion.normalizer import (
    normalize_canonical_dataframe,
    normalize_column_names,
    normalize_dataframe,
)
from src.data.schema import CANONICAL_COLUMNS


@dataclass(frozen=True)
class GenericDataSource(RacingDataSource):
    """Adapter for already-downloaded local CSV files.

    This adapter assumes the performance dataset is intended to represent the
    canonical one-horse-in-one-race table. It therefore runs normalization and
    validation on performance data before returning it.
    """

    performance_data_path: str | Path
    race_data_path: str | Path | None = None
    trackwork_data_path: str | Path | None = None
    odds_data_path: str | Path | None = None
    feature_columns: tuple[str, ...] | None = None

    metadata: ClassVar[SourceMetadata] = SourceMetadata(
        source_name="generic",
        source_type="local_csv",
        country=None,
        racecourse=None,
        supports_results=True,
        supports_trackwork=True,
        supports_ratings=True,
        supports_odds=True,
    )
    field_mappings: ClassVar[dict[str, str]] = {
        column: column for column in CANONICAL_COLUMNS
    }

    @property
    def source_name(self) -> str:
        return self.metadata.source_name

    def load_race_data(self) -> pd.DataFrame:
        if self.race_data_path is None:
            return pd.DataFrame()

        return self._load_generic_csv(
            self.race_data_path,
            date_columns=("race_date",),
            numeric_columns=("race_number", "distance_m", "field_size"),
        )

    def load_performance_data(self) -> pd.DataFrame:
        raw_df = load_csv_file(self.performance_data_path)
        return normalize_canonical_dataframe(
            raw_df,
            feature_columns=self.feature_columns,
        )

    def load_trackwork_data(self) -> pd.DataFrame | None:
        if self.trackwork_data_path is None:
            return None

        return self._load_generic_csv(
            self.trackwork_data_path,
            date_columns=("race_date", "odds_timestamp"),
            numeric_columns=(
                "last_trackwork_distance_m",
                "last_trackwork_time_sec",
                "recent_trackwork_count",
                "days_since_last_trackwork",
            ),
        )

    def load_odds_data(self) -> pd.DataFrame | None:
        if self.odds_data_path is None:
            return None

        return self._load_generic_csv(
            self.odds_data_path,
            date_columns=("race_date", "odds_timestamp"),
            numeric_columns=("opening_odds_decimal", "current_odds_decimal"),
        )

    def _load_generic_csv(
        self,
        path: str | Path,
        *,
        date_columns: tuple[str, ...],
        numeric_columns: tuple[str, ...],
    ) -> pd.DataFrame:
        raw_df = load_csv_file(path)
        normalized_columns = tuple(normalize_column_names(raw_df).columns)
        relevant_dates = tuple(
            column for column in date_columns if column in normalized_columns
        )
        relevant_numeric = tuple(
            column for column in numeric_columns if column in normalized_columns
        )
        return normalize_dataframe(
            raw_df,
            date_columns=relevant_dates,
            numeric_columns=relevant_numeric,
        )
