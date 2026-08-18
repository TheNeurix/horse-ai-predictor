from pathlib import Path

import pandas as pd
import pytest

from src.data.ingestion.csv_loader import (
    CSVFileNotFoundError,
    CSVMalformedError,
    load_csv_file,
)
from src.data.ingestion.normalizer import (
    DatasetComponentPresence,
    identify_dataset_components,
    normalize_canonical_dataframe,
    normalize_column_names,
    normalize_dataframe,
)
from src.data.schema import CANONICAL_COLUMNS


def make_canonical_frame() -> pd.DataFrame:
    row = {column: pd.NA for column in CANONICAL_COLUMNS}
    row.update(
        {
            "race_id": "race-1",
            "race_date": "2026-08-18",
            "racecourse": "course-1",
            "distance_m": "1600",
            "horse_id": "horse-1",
            "horse_name": "runner-1",
        }
    )
    return pd.DataFrame([row], columns=CANONICAL_COLUMNS)


def test_load_csv_file_reads_valid_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("alpha,beta\n1,2\n", encoding="utf-8")

    result = load_csv_file(csv_path)

    assert list(result.columns) == ["alpha", "beta"]
    assert result.iloc[0].to_dict() == {"alpha": 1, "beta": 2}


def test_load_csv_file_raises_for_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(CSVFileNotFoundError, match="does not exist"):
        load_csv_file(missing_path)


def test_load_csv_file_raises_for_malformed_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text('alpha,beta\n"1,2\n', encoding="utf-8")

    with pytest.raises(CSVMalformedError, match="Malformed CSV file"):
        load_csv_file(csv_path)


def test_normalize_column_names_converts_to_snake_case() -> None:
    df = pd.DataFrame(columns=[" Race ID ", "Horse/Name", "Current Odds (Decimal)"])

    normalized = normalize_column_names(df)

    assert list(normalized.columns) == [
        "race_id",
        "horse_name",
        "current_odds_decimal",
    ]


def test_normalize_dataframe_trims_whitespace_and_standardizes_empty_strings() -> None:
    df = pd.DataFrame({"horse_name": ["  runner-1  ", "   ", None]})

    normalized = normalize_dataframe(df)

    assert normalized.loc[0, "horse_name"] == "runner-1"
    assert pd.isna(normalized.loc[1, "horse_name"])
    assert pd.isna(normalized.loc[2, "horse_name"])


def test_normalize_dataframe_converts_dates_consistently() -> None:
    df = pd.DataFrame({"race_date": ["2026/08/18", "2026-08-19", pd.NA]})

    normalized = normalize_dataframe(df, date_columns=["race_date"])

    assert str(normalized["race_date"].dtype).startswith("datetime64")
    assert normalized.loc[0, "race_date"] == pd.Timestamp("2026-08-18")
    assert normalized.loc[1, "race_date"] == pd.Timestamp("2026-08-19")
    assert pd.isna(normalized.loc[2, "race_date"])


def test_normalize_dataframe_converts_numeric_fields_safely() -> None:
    df = pd.DataFrame({"distance_m": ["1600", "1400.5", pd.NA]})

    normalized = normalize_dataframe(df, numeric_columns=["distance_m"])

    assert normalized.loc[0, "distance_m"] == 1600.0
    assert normalized.loc[1, "distance_m"] == 1400.5
    assert pd.isna(normalized.loc[2, "distance_m"])


def test_normalize_dataframe_preserves_missing_values() -> None:
    df = pd.DataFrame({"weight_kg": [pd.NA, "", "  "]})

    normalized = normalize_dataframe(df, numeric_columns=["weight_kg"])

    assert normalized["weight_kg"].isna().all()


def test_identify_dataset_components_reports_present_sections() -> None:
    df = pd.DataFrame(
        columns=[
            "Race ID",
            "Horse ID",
            "Distance M",
            "Current Odds Decimal",
            "Finish Position",
        ]
    )

    components = identify_dataset_components(df)

    assert components == DatasetComponentPresence(
        race_information=True,
        horse_information=True,
        pre_race_features=False,
        result_fields=True,
        market_odds=True,
    )


def test_normalize_canonical_dataframe_integrates_schema_validation() -> None:
    df = make_canonical_frame()

    normalized = normalize_canonical_dataframe(
        df,
        feature_columns=["race_date", "distance_m", "horse_name"],
    )

    assert normalized.loc[0, "distance_m"] == 1600.0
    assert normalized.loc[0, "race_date"] == pd.Timestamp("2026-08-18")
