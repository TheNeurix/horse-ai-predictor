"""Canonical horse-racing dataset schema for MVP 0.1.

The primary prediction unit is one horse in one race. Every row in the
historical dataset must therefore be uniquely identified by:

    race_id + horse_id

This module separates:
1. Pre-race information that is safe to use as model input features.
2. Post-race outcomes that must never be used as model inputs.

Missing values should be represented consistently:
- Use ``pd.NA`` for nullable string/integer/boolean columns.
- Use ``numpy.nan`` / ``pd.NA`` for nullable numeric columns.
- Use ``pd.NaT`` for missing datetime-like values.
- Use ``None`` only at the Python object/dataclass layer before conversion
  into a pandas DataFrame.

Historical form fields must be computed strictly from races that happened
before the current race date/time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd


@dataclass(frozen=True)
class FieldSpec:
    """Metadata for one canonical dataset column."""

    name: str
    group: str
    dtype: str
    nullable: bool
    known_before_race: bool
    description: str


PRIMARY_KEY_COLUMNS: Final[tuple[str, str]] = ("race_id", "horse_id")

RACE_INFORMATION_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("race_id", "race", "string", False, True, "Stable unique race identifier."),
    FieldSpec("race_date", "race", "datetime64[ns]", False, True, "Race calendar date."),
    FieldSpec("racecourse", "race", "string", False, True, "Racecourse or track name."),
    FieldSpec("country", "race", "string", True, True, "Country where the race is run."),
    FieldSpec("race_number", "race", "Int64", True, True, "Race number on the card."),
    FieldSpec("scheduled_time", "race", "string", True, True, "Scheduled local off time."),
    FieldSpec("distance_m", "race", "float64", False, True, "Scheduled race distance in metres."),
    FieldSpec("race_class", "race", "string", True, True, "Declared race class."),
    FieldSpec("race_type", "race", "string", True, True, "Race type such as flat, hurdles, etc."),
    FieldSpec("going", "race", "string", True, True, "Track condition known before the race."),
    FieldSpec("field_size", "race", "Int64", True, True, "Declared number of runners."),
)

HORSE_INFORMATION_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("horse_id", "horse", "string", False, True, "Stable unique horse identifier."),
    FieldSpec("horse_name", "horse", "string", False, True, "Horse display name."),
    FieldSpec("age", "horse", "Int64", True, True, "Horse age at race time."),
    FieldSpec("sex", "horse", "string", True, True, "Horse sex."),
    FieldSpec("sire", "horse", "string", True, True, "Horse sire."),
    FieldSpec("dam", "horse", "string", True, True, "Horse dam."),
)

HANDICAP_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("draw", "handicap", "Int64", True, True, "Barrier or stall draw."),
    FieldSpec("weight_kg", "handicap", "float64", True, True, "Assigned carried weight in kilograms."),
    FieldSpec("handicap_rating", "handicap", "float64", True, True, "Official or handicap rating."),
    FieldSpec("jockey_id", "handicap", "string", True, True, "Stable unique jockey identifier."),
    FieldSpec("jockey_name", "handicap", "string", True, True, "Jockey display name."),
    FieldSpec("trainer_id", "handicap", "string", True, True, "Stable unique trainer identifier."),
    FieldSpec("trainer_name", "handicap", "string", True, True, "Trainer display name."),
    FieldSpec("equipment", "handicap", "string", True, True, "Declared equipment such as blinkers."),
)

HISTORICAL_FORM_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("starts_before_race", "historical_form", "Int64", True, True, "Career starts before this race."),
    FieldSpec("wins_before_race", "historical_form", "Int64", True, True, "Career wins before this race."),
    FieldSpec("places_before_race", "historical_form", "Int64", True, True, "Career placed finishes before this race."),
    FieldSpec("top3_before_race", "historical_form", "Int64", True, True, "Career top-3 finishes before this race."),
    FieldSpec("win_rate_before_race", "historical_form", "float64", True, True, "Wins divided by starts before this race."),
    FieldSpec("top3_rate_before_race", "historical_form", "float64", True, True, "Top-3 finishes divided by starts before this race."),
    FieldSpec("last_finish", "historical_form", "Int64", True, True, "Finish position in the immediately previous race."),
    FieldSpec("last_3_form", "historical_form", "string", True, True, "Compact summary of the last 3 race results."),
    FieldSpec("last_5_form", "historical_form", "string", True, True, "Compact summary of the last 5 race results."),
    FieldSpec("days_since_last_run", "historical_form", "Int64", True, True, "Days since the previous race."),
    FieldSpec("previous_distance_m", "historical_form", "float64", True, True, "Distance of the previous race."),
    FieldSpec("previous_class", "historical_form", "string", True, True, "Class of the previous race."),
    FieldSpec("previous_weight_kg", "historical_form", "float64", True, True, "Weight carried in the previous race."),
    FieldSpec("previous_rating", "historical_form", "float64", True, True, "Official or handicap rating before the previous race."),
)

DISTANCE_COURSE_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("distance_starts_before_race", "distance_course", "Int64", True, True, "Starts at a similar distance before this race."),
    FieldSpec("distance_wins_before_race", "distance_course", "Int64", True, True, "Wins at a similar distance before this race."),
    FieldSpec("distance_top3_before_race", "distance_course", "Int64", True, True, "Top-3 finishes at a similar distance before this race."),
    FieldSpec("course_starts_before_race", "distance_course", "Int64", True, True, "Starts at this course before this race."),
    FieldSpec("course_wins_before_race", "distance_course", "Int64", True, True, "Wins at this course before this race."),
    FieldSpec("course_top3_before_race", "distance_course", "Int64", True, True, "Top-3 finishes at this course before this race."),
)

TRACKWORK_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("days_since_last_trackwork", "trackwork", "Int64", True, True, "Days since the latest trackwork session."),
    FieldSpec("last_trackwork_distance_m", "trackwork", "float64", True, True, "Distance of the latest trackwork session."),
    FieldSpec("last_trackwork_time_sec", "trackwork", "float64", True, True, "Time of the latest trackwork session in seconds."),
    FieldSpec("recent_trackwork_count", "trackwork", "Int64", True, True, "Trackwork sessions recorded in the recent lookback window."),
)

MARKET_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("opening_odds_decimal", "market", "float64", True, True, "Opening market odds in decimal format."),
    FieldSpec("current_odds_decimal", "market", "float64", True, True, "Latest available pre-race market odds in decimal format."),
    FieldSpec("odds_timestamp", "market", "datetime64[ns]", True, True, "Timestamp when the odds snapshot was recorded."),
)

RESULT_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("finish_position", "result", "Int64", True, False, "Official finish position after the race."),
    FieldSpec("beaten_lengths", "result", "float64", True, False, "Beaten lengths after the race."),
    FieldSpec("did_not_finish", "result", "boolean", True, False, "Whether the horse did not finish."),
)

TARGET_FIELDS: Final[tuple[FieldSpec, ...]] = (
    FieldSpec("target_win", "target", "Int64", True, False, "Binary target: 1 if the horse won, else 0."),
    FieldSpec("target_top3", "target", "Int64", True, False, "Binary target: 1 if the horse finished in the top 3, else 0."),
)

SCHEMA_FIELDS: Final[tuple[FieldSpec, ...]] = (
    RACE_INFORMATION_FIELDS
    + HORSE_INFORMATION_FIELDS
    + HANDICAP_FIELDS
    + HISTORICAL_FORM_FIELDS
    + DISTANCE_COURSE_FIELDS
    + TRACKWORK_FIELDS
    + MARKET_FIELDS
    + RESULT_FIELDS
    + TARGET_FIELDS
)

CANONICAL_COLUMNS: Final[tuple[str, ...]] = tuple(field.name for field in SCHEMA_FIELDS)
PRE_RACE_COLUMNS: Final[tuple[str, ...]] = tuple(
    field.name for field in SCHEMA_FIELDS if field.known_before_race
)
POST_RACE_COLUMNS: Final[tuple[str, ...]] = tuple(
    field.name for field in SCHEMA_FIELDS if not field.known_before_race
)
PROHIBITED_FEATURE_COLUMNS: Final[tuple[str, ...]] = POST_RACE_COLUMNS


def schema_dataframe() -> pd.DataFrame:
    """Return the schema definition as a pandas DataFrame for inspection."""

    return pd.DataFrame([field.__dict__ for field in SCHEMA_FIELDS])


def empty_canonical_dataframe() -> pd.DataFrame:
    """Return an empty canonical DataFrame with the expected column order."""

    return pd.DataFrame(columns=CANONICAL_COLUMNS)
