"""Generic normalization helpers for source-specific racing datasets."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final

import pandas as pd

from src.data.schema import (
    HANDICAP_FIELDS,
    HISTORICAL_FORM_FIELDS,
    MARKET_FIELDS,
    RACE_INFORMATION_FIELDS,
    RESULT_FIELDS,
    SCHEMA_FIELDS,
    TARGET_FIELDS,
    TRACKWORK_FIELDS,
    DISTANCE_COURSE_FIELDS,
    HORSE_INFORMATION_FIELDS,
)
from src.data.validation import validate_canonical_dataframe


class NormalizationError(ValueError):
    """Raised when source data cannot be normalized safely."""


@dataclass(frozen=True)
class DatasetComponentPresence:
    """Boolean summary of which canonical data components are present."""

    race_information: bool
    horse_information: bool
    pre_race_features: bool
    result_fields: bool
    market_odds: bool


_NON_ALPHANUMERIC_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9]+")
_RACE_INFORMATION_COLUMNS: Final[set[str]] = {
    field.name for field in RACE_INFORMATION_FIELDS
}
_HORSE_INFORMATION_COLUMNS: Final[set[str]] = {
    field.name for field in HORSE_INFORMATION_FIELDS
}
_PRE_RACE_FEATURE_COLUMNS: Final[set[str]] = {
    field.name
    for field in (
        HANDICAP_FIELDS
        + HISTORICAL_FORM_FIELDS
        + DISTANCE_COURSE_FIELDS
        + TRACKWORK_FIELDS
    )
}
_RESULT_COLUMNS: Final[set[str]] = {
    field.name for field in RESULT_FIELDS + TARGET_FIELDS
}
_MARKET_COLUMNS: Final[set[str]] = {field.name for field in MARKET_FIELDS}
_CANONICAL_DATE_COLUMNS: Final[tuple[str, ...]] = tuple(
    field.name
    for field in SCHEMA_FIELDS
    if field.dtype.startswith("datetime64")
)
_CANONICAL_NUMERIC_DTYPES: Final[dict[str, str]] = {
    field.name: field.dtype
    for field in SCHEMA_FIELDS
    if field.dtype in {"float64", "Int64"}
}


def normalize_column_name(name: str) -> str:
    """Normalize a source column name into snake_case."""

    normalized = _NON_ALPHANUMERIC_PATTERN.sub("_", name.strip().lower()).strip("_")
    if not normalized:
        raise NormalizationError("Column name cannot be empty after normalization.")
    return normalized


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized snake_case column names."""

    renamed_columns = [normalize_column_name(str(column)) for column in df.columns]
    if len(renamed_columns) != len(set(renamed_columns)):
        raise NormalizationError(
            "Column normalization produced duplicate column names."
        )

    normalized_df = df.copy()
    normalized_df.columns = renamed_columns
    return normalized_df


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Trim leading and trailing whitespace from string-like fields."""

    normalized_df = df.copy()
    for column in normalized_df.columns:
        normalized_df[column] = normalized_df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return normalized_df


def standardize_empty_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Convert empty strings to missing values without inventing replacements."""

    normalized_df = df.copy()
    for column in normalized_df.columns:
        normalized_df[column] = normalized_df[column].map(
            lambda value: pd.NA if isinstance(value, str) and value == "" else value
        )
    return normalized_df


def normalize_dates(
    df: pd.DataFrame, date_columns: list[str] | tuple[str, ...] | None = None
) -> pd.DataFrame:
    """Parse datetime-like columns into pandas datetime values."""

    normalized_df = df.copy()
    columns = list(date_columns or [])

    for column in columns:
        if column not in normalized_df.columns:
            continue

        source = normalized_df[column]
        try:
            parsed = pd.to_datetime(source, errors="coerce", format="mixed")
        except TypeError:
            parsed = pd.to_datetime(source, errors="coerce")
        invalid = source.notna() & parsed.isna()
        if invalid.any():
            invalid_values = source.loc[invalid].tolist()
            raise NormalizationError(
                f"Column {column} contains invalid date values: {invalid_values}"
            )

        normalized_df[column] = parsed

    return normalized_df


def convert_numeric_columns(
    df: pd.DataFrame,
    numeric_columns: list[str] | tuple[str, ...],
    dtype_overrides: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Safely convert numeric columns while preserving missing values."""

    normalized_df = df.copy()

    for column in numeric_columns:
        if column not in normalized_df.columns:
            continue

        source = normalized_df[column]
        parsed = pd.to_numeric(source, errors="coerce")
        invalid = source.notna() & parsed.isna()
        if invalid.any():
            invalid_values = source.loc[invalid].tolist()
            raise NormalizationError(
                f"Column {column} contains invalid numeric values: {invalid_values}"
            )

        target_dtype = None if dtype_overrides is None else dtype_overrides.get(column)
        if target_dtype == "Int64":
            normalized_df[column] = parsed.astype("Int64")
        elif target_dtype == "float64":
            normalized_df[column] = parsed.astype("float64")
        else:
            normalized_df[column] = parsed

    return normalized_df


def normalize_dataframe(
    df: pd.DataFrame,
    date_columns: list[str] | tuple[str, ...] | None = None,
    numeric_columns: list[str] | tuple[str, ...] | None = None,
    dtype_overrides: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Apply generic normalization steps to a source DataFrame."""

    normalized_df = normalize_column_names(df)
    normalized_df = trim_whitespace(normalized_df)
    normalized_df = standardize_empty_strings(normalized_df)
    normalized_df = normalize_dates(normalized_df, date_columns=date_columns)

    if numeric_columns:
        normalized_df = convert_numeric_columns(
            normalized_df,
            numeric_columns=numeric_columns,
            dtype_overrides=dtype_overrides,
        )

    return normalized_df


def identify_dataset_components(df: pd.DataFrame) -> DatasetComponentPresence:
    """Identify which canonical data components are represented by the columns."""

    normalized_columns = set(normalize_column_names(df).columns)
    return DatasetComponentPresence(
        race_information=bool(normalized_columns & _RACE_INFORMATION_COLUMNS),
        horse_information=bool(normalized_columns & _HORSE_INFORMATION_COLUMNS),
        pre_race_features=bool(normalized_columns & _PRE_RACE_FEATURE_COLUMNS),
        result_fields=bool(normalized_columns & _RESULT_COLUMNS),
        market_odds=bool(normalized_columns & _MARKET_COLUMNS),
    )


def normalize_canonical_dataframe(
    df: pd.DataFrame, feature_columns: list[str] | tuple[str, ...] | None = None
) -> pd.DataFrame:
    """Normalize and validate a DataFrame intended for the canonical schema."""

    normalized_df = normalize_dataframe(
        df,
        date_columns=_CANONICAL_DATE_COLUMNS,
        numeric_columns=tuple(_CANONICAL_NUMERIC_DTYPES.keys()),
        dtype_overrides=_CANONICAL_NUMERIC_DTYPES,
    )
    validate_canonical_dataframe(normalized_df, feature_columns=feature_columns)
    return normalized_df
