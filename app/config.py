"""Application configuration utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime configuration values."""

    golden_source_path: Path
    fuzzy_match_threshold: int = 92
    default_state: str = "FL"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables or default values."""

    project_root = Path(__file__).resolve().parent.parent
    golden_source = Path(
        os.getenv("GOLDEN_SOURCE_PATH", project_root / "PinellasCount_Extract.xlsx")
    )
    threshold = int(os.getenv("FUZZY_MATCH_THRESHOLD", "92"))
    default_state = os.getenv("DEFAULT_STATE", "FL")
    return Settings(
        golden_source_path=golden_source,
        fuzzy_match_threshold=threshold,
        default_state=default_state,
    )
