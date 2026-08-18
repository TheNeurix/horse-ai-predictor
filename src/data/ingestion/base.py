"""Abstract interfaces for historical racing data ingestion."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class RacingDataSource(ABC):
    """Contract for a source that exposes raw racing data tables.

    Concrete adapters can later load data from vendor exports, local files,
    APIs, or other systems, but they must all return pandas DataFrames that
    can be normalized into the canonical horse-race schema.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return a human-readable source name."""

    @abstractmethod
    def load_race_data(self) -> pd.DataFrame:
        """Load race-level source data."""

    @abstractmethod
    def load_performance_data(self) -> pd.DataFrame:
        """Load horse-in-race performance source data."""

    def load_trackwork_data(self) -> pd.DataFrame | None:
        """Load optional trackwork data when the source provides it."""

        return None

    def load_odds_data(self) -> pd.DataFrame | None:
        """Load optional market odds data when the source provides it."""

        return None
