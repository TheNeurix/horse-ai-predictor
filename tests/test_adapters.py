from pathlib import Path
import socket

import pandas as pd
import pytest

from src.data.ingestion.adapters import (
    SOURCE_REGISTRY,
    GenericDataSource,
    RCTCDataSource,
    create_data_source,
    get_source_registry,
)
from src.data.schema import CANONICAL_COLUMNS
from src.data.validation import SchemaValidationError


def write_canonical_csv(path: Path) -> None:
    row = {column: pd.NA for column in CANONICAL_COLUMNS}
    row.update(
        {
            "race_id": "RACE-001",
            "race_date": "2026-08-18",
            "racecourse": "Test Course",
            "distance_m": "1600",
            "horse_id": "HORSE-001",
            "horse_name": "Runner 1",
        }
    )
    pd.DataFrame([row], columns=CANONICAL_COLUMNS).to_csv(path, index=False)


def test_generic_adapter_can_be_instantiated_and_load_local_csvs(
    tmp_path: Path,
) -> None:
    performance_path = tmp_path / "performance.csv"
    race_path = tmp_path / "race.csv"
    write_canonical_csv(performance_path)
    pd.DataFrame(
        [{"Race Date": "2026-08-18", "Race Number": "1", "Distance M": "1600"}]
    ).to_csv(race_path, index=False)

    adapter = GenericDataSource(
        performance_data_path=performance_path,
        race_data_path=race_path,
        feature_columns=("race_date", "distance_m", "horse_name"),
    )

    performance_df = adapter.load_performance_data()
    race_df = adapter.load_race_data()

    assert adapter.source_name == "generic"
    assert performance_df.loc[0, "race_date"] == pd.Timestamp("2026-08-18")
    assert performance_df.loc[0, "distance_m"] == 1600.0
    assert list(race_df.columns) == ["race_date", "race_number", "distance_m"]


def test_generic_adapter_uses_validation_pipeline(tmp_path: Path) -> None:
    performance_path = tmp_path / "invalid-performance.csv"
    pd.DataFrame(
        [{"race_id": "RACE-001", "horse_id": "HORSE-001", "distance_m": 1600}]
    ).to_csv(performance_path, index=False)

    adapter = GenericDataSource(performance_data_path=performance_path)

    with pytest.raises(SchemaValidationError, match="Missing required columns"):
        adapter.load_performance_data()


def test_rctc_adapter_can_be_instantiated() -> None:
    adapter = RCTCDataSource()

    assert adapter.source_name == "rctc"
    assert adapter.expected_components == (
        "entries",
        "race_card",
        "handicap",
        "acceptance",
        "revised_ratings",
        "race_result",
        "trackwork",
    )


def test_registry_returns_expected_adapters() -> None:
    registry = get_source_registry()

    assert registry == SOURCE_REGISTRY
    assert set(registry) == {"generic", "rctc"}
    assert registry["generic"] is GenericDataSource
    assert registry["rctc"] is RCTCDataSource


def test_create_data_source_instantiates_registered_adapter(tmp_path: Path) -> None:
    performance_path = tmp_path / "performance.csv"
    write_canonical_csv(performance_path)

    adapter = create_data_source(
        "generic",
        performance_data_path=performance_path,
    )

    assert isinstance(adapter, GenericDataSource)


def test_adapter_metadata_is_available() -> None:
    assert GenericDataSource.metadata.source_type == "local_csv"
    assert GenericDataSource.metadata.supports_odds is True
    assert RCTCDataSource.metadata.country == "India"
    assert RCTCDataSource.metadata.racecourse == "Royal Calcutta Turf Club"


def test_adapter_mappings_exist() -> None:
    assert GenericDataSource.field_mappings["horse_name"] == "horse_name"
    assert RCTCDataSource.field_mappings["entries"]["<source horse name>"] == "horse_name"
    assert (
        RCTCDataSource.field_mappings["race_result"]["<source finish position>"]
        == "finish_position"
    )


def test_adapters_do_not_make_network_calls_during_instantiation_or_local_loading(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    performance_path = tmp_path / "performance.csv"
    write_canonical_csv(performance_path)

    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("Unexpected external network call.")

    monkeypatch.setattr(socket, "create_connection", fail_network)

    generic_adapter = GenericDataSource(performance_data_path=performance_path)
    rctc_adapter = RCTCDataSource()

    loaded_df = generic_adapter.load_performance_data()

    assert loaded_df.loc[0, "horse_id"] == "HORSE-001"
    assert rctc_adapter.metadata.supports_results is True
