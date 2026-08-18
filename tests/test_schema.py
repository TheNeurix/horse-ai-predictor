import pandas as pd
import pytest

from src.data.schema import CANONICAL_COLUMNS, POST_RACE_COLUMNS, PRE_RACE_COLUMNS
from src.data.validation import (
    SchemaValidationError,
    check_dates,
    check_distance_is_positive,
    check_finish_position_is_positive,
    check_odds_are_positive,
    check_race_horse_uniqueness,
    check_required_columns,
    check_target_top3_binary,
    check_target_win_binary,
    check_weight_is_positive,
    detect_leakage_fields,
    validate_canonical_dataframe,
)


def make_valid_dataframe() -> pd.DataFrame:
    row = {
        "race_id": "RACE-001",
        "race_date": "2026-08-18",
        "racecourse": "Ascot",
        "country": "GB",
        "race_number": 1,
        "scheduled_time": "15:30:00",
        "distance_m": 1600.0,
        "race_class": "Class 3",
        "race_type": "Flat",
        "going": "Good",
        "field_size": 12,
        "horse_id": "HORSE-001",
        "horse_name": "Example Runner",
        "age": 4,
        "sex": "Gelding",
        "sire": "Example Sire",
        "dam": "Example Dam",
        "draw": 4,
        "weight_kg": 57.0,
        "handicap_rating": 84.0,
        "jockey_id": "JOCKEY-001",
        "jockey_name": "A. Rider",
        "trainer_id": "TRAINER-001",
        "trainer_name": "B. Trainer",
        "equipment": pd.NA,
        "starts_before_race": 10,
        "wins_before_race": 2,
        "places_before_race": 4,
        "top3_before_race": 5,
        "win_rate_before_race": 0.2,
        "top3_rate_before_race": 0.5,
        "last_finish": 3,
        "last_3_form": "3-1-2",
        "last_5_form": "3-1-2-4-5",
        "days_since_last_run": 21,
        "previous_distance_m": 1400.0,
        "previous_class": "Class 3",
        "previous_weight_kg": 56.5,
        "previous_rating": 83.0,
        "distance_starts_before_race": 4,
        "distance_wins_before_race": 1,
        "distance_top3_before_race": 2,
        "course_starts_before_race": 2,
        "course_wins_before_race": 0,
        "course_top3_before_race": 1,
        "days_since_last_trackwork": 3,
        "last_trackwork_distance_m": 1000.0,
        "last_trackwork_time_sec": 61.8,
        "recent_trackwork_count": 2,
        "opening_odds_decimal": 7.5,
        "current_odds_decimal": 6.8,
        "odds_timestamp": "2026-08-18T14:45:00",
        "finish_position": 2,
        "beaten_lengths": 1.25,
        "did_not_finish": 0,
        "target_win": 0,
        "target_top3": 1,
    }
    return pd.DataFrame([row], columns=CANONICAL_COLUMNS)


def test_canonical_columns_are_split_between_pre_and_post_race() -> None:
    assert "finish_position" in POST_RACE_COLUMNS
    assert "target_win" in POST_RACE_COLUMNS
    assert "race_date" in PRE_RACE_COLUMNS
    assert "current_odds_decimal" in PRE_RACE_COLUMNS


def test_validate_canonical_dataframe_accepts_valid_data() -> None:
    df = make_valid_dataframe()
    validate_canonical_dataframe(
        df,
        feature_columns=["race_date", "distance_m", "current_odds_decimal"],
    )


def test_check_required_columns_raises_for_missing_column() -> None:
    df = make_valid_dataframe().drop(columns=["trainer_name"])
    with pytest.raises(SchemaValidationError, match="Missing required columns"):
        check_required_columns(df)


def test_check_race_horse_uniqueness_raises_for_duplicate_key() -> None:
    df = pd.concat([make_valid_dataframe(), make_valid_dataframe()], ignore_index=True)
    with pytest.raises(
        SchemaValidationError, match="Duplicate race_id \\+ horse_id combinations"
    ):
        check_race_horse_uniqueness(df)


def test_check_dates_raises_for_invalid_race_date() -> None:
    df = make_valid_dataframe()
    df.loc[0, "race_date"] = "not-a-date"
    with pytest.raises(SchemaValidationError, match="Invalid datetime values"):
        check_dates(df)


def test_check_distance_is_positive_raises_for_non_positive_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "distance_m"] = 0
    with pytest.raises(SchemaValidationError, match="distance_m must be positive"):
        check_distance_is_positive(df)


def test_check_weight_is_positive_raises_for_negative_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "weight_kg"] = -1
    with pytest.raises(SchemaValidationError, match="weight_kg must be positive"):
        check_weight_is_positive(df)


def test_check_odds_are_positive_raises_for_invalid_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "opening_odds_decimal"] = 0
    with pytest.raises(
        SchemaValidationError, match="opening_odds_decimal must be positive"
    ):
        check_odds_are_positive(df)


def test_check_finish_position_is_positive_raises_for_invalid_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "finish_position"] = -2
    with pytest.raises(
        SchemaValidationError, match="finish_position must be positive"
    ):
        check_finish_position_is_positive(df)


def test_check_target_win_binary_raises_for_invalid_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "target_win"] = 2
    with pytest.raises(SchemaValidationError, match="target_win must contain only 0 or 1"):
        check_target_win_binary(df)


def test_check_target_top3_binary_raises_for_invalid_value() -> None:
    df = make_valid_dataframe()
    df.loc[0, "target_top3"] = -1
    with pytest.raises(
        SchemaValidationError, match="target_top3 must contain only 0 or 1"
    ):
        check_target_top3_binary(df)


def test_detect_leakage_fields_rejects_post_race_columns() -> None:
    with pytest.raises(
        SchemaValidationError, match="Feature list contains post-race leakage fields"
    ):
        detect_leakage_fields(["distance_m", "finish_position", "target_top3"])
