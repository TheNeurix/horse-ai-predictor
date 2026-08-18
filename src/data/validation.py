"""Validation helpers for the canonical horse-racing dataset."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import pandas as pd

from src.data.schema import CANONICAL_COLUMNS, PRIMARY_KEY_COLUMNS, PROHIBITED_FEATURE_COLUMNS


class SchemaValidationError(ValueError):
    """Raised when a canonical racing DataFrame violates schema rules."""


def check_required_columns(
    df: pd.DataFrame, required_columns: Sequence[str] = CANONICAL_COLUMNS
) -> None:
    """Ensure all required columns exist, even if some values are missing."""

    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise SchemaValidationError(f"Missing required columns: {missing}")


def check_race_horse_uniqueness(df: pd.DataFrame) -> None:
    """Ensure the prediction unit (race_id + horse_id) is unique."""

    duplicated = df.duplicated(subset=list(PRIMARY_KEY_COLUMNS), keep=False)
    if duplicated.any():
        duplicates = df.loc[duplicated, list(PRIMARY_KEY_COLUMNS)].to_dict("records")
        raise SchemaValidationError(
            "Duplicate race_id + horse_id combinations found: "
            f"{duplicates}"
        )


def check_dates(df: pd.DataFrame) -> None:
    """Validate datetime-like columns used by the canonical dataset."""

    for column in ("race_date", "odds_timestamp"):
        if column not in df.columns:
            continue

        series = df[column]
        parsed = pd.to_datetime(series, errors="coerce")
        invalid = series.notna() & parsed.isna()
        if invalid.any():
            bad_values = series.loc[invalid].tolist()
            raise SchemaValidationError(
                f"Invalid datetime values in {column}: {bad_values}"
            )


def _check_positive_when_present(df: pd.DataFrame, column: str) -> None:
    if column not in df.columns:
        return

    values = pd.to_numeric(df[column], errors="coerce")
    invalid = df[column].notna() & ((values.isna()) | (values <= 0))
    if invalid.any():
        bad_values = df.loc[invalid, column].tolist()
        raise SchemaValidationError(
            f"Column {column} must be positive when present. Invalid values: {bad_values}"
        )


def check_distance_is_positive(df: pd.DataFrame) -> None:
    _check_positive_when_present(df, "distance_m")


def check_weight_is_positive(df: pd.DataFrame) -> None:
    _check_positive_when_present(df, "weight_kg")


def check_odds_are_positive(df: pd.DataFrame) -> None:
    for column in ("opening_odds_decimal", "current_odds_decimal"):
        _check_positive_when_present(df, column)


def check_finish_position_is_positive(df: pd.DataFrame) -> None:
    _check_positive_when_present(df, "finish_position")


def _check_binary_target(df: pd.DataFrame, column: str) -> None:
    if column not in df.columns:
        return

    invalid = df[column].notna() & ~df[column].isin([0, 1])
    if invalid.any():
        bad_values = df.loc[invalid, column].tolist()
        raise SchemaValidationError(
            f"Column {column} must contain only 0 or 1 when present. "
            f"Invalid values: {bad_values}"
        )


def check_target_win_binary(df: pd.DataFrame) -> None:
    _check_binary_target(df, "target_win")


def check_target_top3_binary(df: pd.DataFrame) -> None:
    _check_binary_target(df, "target_top3")


def detect_leakage_fields(feature_columns: Iterable[str]) -> None:
    """Reject post-race columns when a caller builds a feature list."""

    leakage = sorted(set(feature_columns) & set(PROHIBITED_FEATURE_COLUMNS))
    if leakage:
        raise SchemaValidationError(
            "Feature list contains post-race leakage fields: "
            f"{leakage}"
        )


def validate_canonical_dataframe(
    df: pd.DataFrame, feature_columns: Iterable[str] | None = None
) -> None:
    """Run the full canonical schema validation suite."""

    check_required_columns(df)
    check_race_horse_uniqueness(df)
    check_dates(df)
    check_distance_is_positive(df)
    check_weight_is_positive(df)
    check_odds_are_positive(df)
    check_finish_position_is_positive(df)
    check_target_win_binary(df)
    check_target_top3_binary(df)
    if feature_columns is not None:
        detect_leakage_fields(feature_columns)
