"""Pydantic models used by the FastAPI service."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class AddressMatchRequest(BaseModel):
    address: str = Field(..., description="Full free-form US address provided by the user.")


class AddressMatchResponse(BaseModel):
    match_type: Literal["exact_match", "fuzzy_match", "no_match"]
    confidence: float = Field(ge=0.0, le=1.0)
    input_address: str
    normalized_input: str
    matched_address: Optional[str] = None
    golden_record: Optional[Dict[str, Any]] = None
