"""Royal Calcutta Turf Club source adapter definition.

This module intentionally does not fetch or scrape the RCTC website in MVP 0.1.
It only captures the adapter contract, source metadata, expected source
components, and placeholder field mappings needed for future implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import pandas as pd

from src.data.ingestion.base import RacingDataSource, SourceMetadata


RCTC_EXPECTED_COMPONENTS: tuple[str, ...] = (
    "entries",
    "race_card",
    "handicap",
    "acceptance",
    "revised_ratings",
    "race_result",
    "trackwork",
)

RCTC_FIELD_MAPPINGS: dict[str, dict[str, str]] = {
    "entries": {
        "<source horse name>": "horse_name",
        "<source horse id or registration id>": "horse_id",
        "<source race date>": "race_date",
        "<source race number>": "race_number",
        "<source racecourse>": "racecourse",
    },
    "race_card": {
        "<source distance>": "distance_m",
        "<source race type>": "race_type",
        "<source scheduled time>": "scheduled_time",
        "<source draw>": "draw",
        "<source equipment>": "equipment",
    },
    "handicap": {
        "<source weight>": "weight_kg",
        "<source rating>": "handicap_rating",
        "<source jockey>": "jockey_name",
        "<source trainer>": "trainer_name",
    },
    "acceptance": {
        "<source field size>": "field_size",
        "<source going>": "going",
        "<source class>": "race_class",
    },
    "revised_ratings": {
        "<source revised rating>": "handicap_rating",
        "<source prior rating>": "previous_rating",
    },
    "race_result": {
        "<source finish position>": "finish_position",
        "<source beaten lengths>": "beaten_lengths",
        "<source did not finish flag>": "did_not_finish",
        "<source win target derived after result>": "target_win",
        "<source top3 target derived after result>": "target_top3",
    },
    "trackwork": {
        "<source trackwork distance>": "last_trackwork_distance_m",
        "<source trackwork time>": "last_trackwork_time_sec",
        "<source trackwork recency>": "days_since_last_trackwork",
        "<source recent trackwork count>": "recent_trackwork_count",
    },
}


@dataclass(frozen=True)
class RCTCDataSource(RacingDataSource):
    """Planned adapter for Royal Calcutta Turf Club racing data."""

    component_paths: dict[str, str | Path] = field(default_factory=dict)

    metadata: ClassVar[SourceMetadata] = SourceMetadata(
        source_name="rctc",
        source_type="planned_public_racing_source",
        country="India",
        racecourse="Royal Calcutta Turf Club",
        supports_results=True,
        supports_trackwork=True,
        supports_ratings=True,
        supports_odds=False,
    )
    expected_components: ClassVar[tuple[str, ...]] = RCTC_EXPECTED_COMPONENTS
    field_mappings: ClassVar[dict[str, dict[str, str]]] = RCTC_FIELD_MAPPINGS

    @property
    def source_name(self) -> str:
        return self.metadata.source_name

    def load_race_data(self) -> pd.DataFrame:
        raise NotImplementedError(
            "RCTCDataSource does not fetch or parse live/public source data yet."
        )

    def load_performance_data(self) -> pd.DataFrame:
        raise NotImplementedError(
            "RCTCDataSource does not fetch or parse live/public source data yet."
        )

    def load_trackwork_data(self) -> pd.DataFrame | None:
        raise NotImplementedError(
            "RCTCDataSource does not fetch or parse live/public source data yet."
        )

    def load_odds_data(self) -> pd.DataFrame | None:
        return None
