"""Pydantic models used by the FastAPI service."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AddressMatchCandidate(BaseModel):
    matched_address: str
    confidence: float = Field(ge=0.0, le=1.0)
    golden_record: Dict[str, Any]


class AddressMatchRequest(BaseModel):
    address: str = Field(..., description="Full free-form US address provided by the user.")


class AddressMatchResponse(BaseModel):
    match_type: Literal["exact_match", "fuzzy_match", "no_match"]
    confidence: float = Field(ge=0.0, le=1.0)
    input_address: str
    normalized_input: str
    matched_address: Optional[str] = None
    golden_record: Optional[Dict[str, Any]] = None
    match_count: int = Field(ge=0)
    matches: List[AddressMatchCandidate] = Field(
        default_factory=list,
        description="All addresses that satisfied the matching criteria.",
    )
