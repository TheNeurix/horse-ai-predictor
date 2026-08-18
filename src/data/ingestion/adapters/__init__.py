"""Source-adapter registry for racing data ingestion."""

from __future__ import annotations

from typing import Final

from src.data.ingestion.adapters.generic import GenericDataSource
from src.data.ingestion.adapters.rctc import RCTCDataSource
from src.data.ingestion.base import RacingDataSource


SOURCE_REGISTRY: Final[dict[str, type[RacingDataSource]]] = {
    "generic": GenericDataSource,
    "rctc": RCTCDataSource,
}


def get_source_registry() -> dict[str, type[RacingDataSource]]:
    """Return the currently registered data-source adapters."""

    return dict(SOURCE_REGISTRY)


def create_data_source(adapter_name: str, **kwargs: object) -> RacingDataSource:
    """Instantiate a registered adapter by name."""

    registry = get_source_registry()
    if adapter_name not in registry:
        available = ", ".join(sorted(registry))
        raise KeyError(
            f"Unknown data-source adapter: {adapter_name}. Available adapters: {available}"
        )
    return registry[adapter_name](**kwargs)


__all__ = [
    "GenericDataSource",
    "RCTCDataSource",
    "SOURCE_REGISTRY",
    "create_data_source",
    "get_source_registry",
]
