"""FastAPI service entrypoint for the address matching application."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI

from .config import get_settings
from .matcher import MatchResult, get_matcher
from .models import AddressMatchRequest, AddressMatchResponse

settings = get_settings()
app = FastAPI(
    title="Golden Source Address Matcher",
    version="1.0.0",
    description=(
        "Service that compares user-provided addresses against the Pinellas County "
        "golden source using exact and fuzzy logic."
    ),
)


@app.on_event("startup")
def _warm_cache() -> None:
    # Ensure the matcher is ready before the first request arrives.
    get_matcher()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/match", response_model=AddressMatchResponse, tags=["matching"])
def match_address(payload: AddressMatchRequest) -> AddressMatchResponse:
    matcher = get_matcher()
    result: MatchResult = matcher.match(payload.address)
    return AddressMatchResponse(**asdict(result))
