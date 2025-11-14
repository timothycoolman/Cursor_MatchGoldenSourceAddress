"""Core matching logic for aligning user input with the golden source."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rapidfuzz import fuzz, process

from .config import Settings, get_settings
from .normalizer import normalize_address


@dataclass
class MatchResult:
    """Structured result returned by the matcher."""

    match_type: str
    confidence: float
    input_address: str
    normalized_input: str
    matched_address: Optional[str]
    golden_record: Optional[Dict[str, Any]]


class AddressMatcher:
    """Encapsulates the logic for matching addresses against the golden source."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._records: List[Dict[str, Any]] = []
        self._choices: List[str] = []
        self._exact_lookup: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data(self.settings.golden_source_path)

    def _load_data(self, source_path: Path) -> None:
        if not source_path.exists():
            raise FileNotFoundError(f"Golden source not found at {source_path}")

        df = pd.read_excel(source_path, engine="openpyxl")
        for _, row in df.iterrows():
            record = {column: _sanitize_value(row[column]) for column in df.columns}
            comparable_address = _compose_full_address(record, self.settings.default_state)
            normalized = normalize_address(comparable_address)
            if not normalized:
                continue

            entry = {
                "normalized": normalized,
                "display_address": comparable_address,
                "record": record,
            }
            self._records.append(entry)
            self._choices.append(normalized)
            self._exact_lookup.setdefault(normalized, []).append(entry)

    def match(self, input_address: str) -> MatchResult:
        if not input_address or not input_address.strip():
            return MatchResult(
                match_type="no_match",
                confidence=0.0,
                input_address=input_address,
                normalized_input="",
                matched_address=None,
                golden_record=None,
            )

        normalized_input = normalize_address(input_address)
        if not normalized_input:
            return MatchResult(
                match_type="no_match",
                confidence=0.0,
                input_address=input_address,
                normalized_input=normalized_input,
                matched_address=None,
                golden_record=None,
            )

        exact_candidates = self._exact_lookup.get(normalized_input)
        if exact_candidates:
            # Return the first exact match; deterministic because of load order.
            entry = exact_candidates[0]
            return MatchResult(
                match_type="exact_match",
                confidence=1.0,
                input_address=input_address,
                normalized_input=normalized_input,
                matched_address=entry["display_address"],
                golden_record=entry["record"],
            )

        best_match = process.extractOne(
            normalized_input,
            self._choices,
            scorer=fuzz.WRatio,
        )

        if not best_match:
            return MatchResult(
                match_type="no_match",
                confidence=0.0,
                input_address=input_address,
                normalized_input=normalized_input,
                matched_address=None,
                golden_record=None,
            )

        _, score, index = best_match
        if score < self.settings.fuzzy_match_threshold:
            return MatchResult(
                match_type="no_match",
                confidence=score / 100.0,
                input_address=input_address,
                normalized_input=normalized_input,
                matched_address=None,
                golden_record=None,
            )

        entry = self._records[index]
        return MatchResult(
            match_type="fuzzy_match",
            confidence=score / 100.0,
            input_address=input_address,
            normalized_input=normalized_input,
            matched_address=entry["display_address"],
            golden_record=entry["record"],
        )


def _compose_full_address(record: Dict[str, Any], default_state: str) -> str:
    """Construct a comparable address string using the available columns."""

    if record.get("Full Address"):
        base = str(record["Full Address"]).strip()
    else:
        number = _ensure_string(record.get("Full Address Number"))
        prefix = _ensure_string(record.get("Prefix"))
        street_name = _ensure_string(record.get("Street Name"))
        street_type = _ensure_string(record.get("Street Type"))
        suffix = _ensure_string(record.get("Suffix"))
        unit_type = _ensure_string(record.get("Address Unit Type"))
        unit_number = _ensure_string(record.get("Address Unit Number"))
        parts = [number, prefix, street_name, street_type, suffix]
        if unit_type or unit_number:
            parts.append(unit_type)
            parts.append(unit_number)
        base = " ".join(part for part in parts if part).strip()

    locality = (
        _ensure_string(record.get("Municipality Name"))
        or _ensure_string(record.get("Mailing City"))
        or _ensure_string(record.get("Place Name"))
    )
    zipcode = _format_zip(record.get("Zipcode"))
    state = _ensure_string(record.get("State")) or default_state

    composite_parts = [base]
    if locality:
        composite_parts.append(locality)
    if state:
        composite_parts.append(state)
    if zipcode:
        composite_parts.append(zipcode)

    return " ".join(part for part in composite_parts if part)


def _ensure_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _format_zip(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        zip_int = int(float(value))
    except (ValueError, TypeError):
        return str(value).strip()
    return f"{zip_int:05d}"


def _sanitize_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


@lru_cache(maxsize=1)
def get_matcher() -> AddressMatcher:
    """Return a cached matcher instance for reuse across requests."""

    return AddressMatcher()
