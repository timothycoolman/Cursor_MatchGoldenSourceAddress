"""Helpers for cleaning and normalizing address text."""

from __future__ import annotations

import re
from typing import Iterable


def _apply_replacements(value: str, replacements: Iterable[tuple[str, str]]) -> str:
    updated = value
    for original, replacement in replacements:
        updated = updated.replace(original, replacement)
    return updated


_COMMON_REPLACEMENTS = (
    (" APARTMENT ", " APT "),
    (" APARTMENTS ", " APT "),
    (" BUILDING ", " BLDG "),
    (" FLOOR ", " FLR "),
    (" MOUNT ", " MT "),
    (" SAINT ", " ST "),
    (" ROAD ", " RD "),
    (" STREET ", " ST "),
    (" AVENUE ", " AVE "),
    (" BOULEVARD ", " BLVD "),
    (" PLACE ", " PL "),
    (" DRIVE ", " DR "),
    (" COURT ", " CT "),
    (" LANE ", " LN "),
    (" TRAIL ", " TRL "),
)

_STATE_REPLACEMENTS = (
    (" FLORIDA", " FL"),
    (" ALABAMA", " AL"),
    (" ALASKA", " AK"),
    (" ARIZONA", " AZ"),
    (" ARKANSAS", " AR"),
    (" CALIFORNIA", " CA"),
    (" COLORADO", " CO"),
    (" CONNECTICUT", " CT"),
    (" DELAWARE", " DE"),
    (" DISTRICT OF COLUMBIA", " DC"),
    (" GEORGIA", " GA"),
    (" HAWAII", " HI"),
    (" IDAHO", " ID"),
    (" ILLINOIS", " IL"),
    (" INDIANA", " IN"),
    (" IOWA", " IA"),
    (" KANSAS", " KS"),
    (" KENTUCKY", " KY"),
    (" LOUISIANA", " LA"),
    (" MAINE", " ME"),
    (" MARYLAND", " MD"),
    (" MASSACHUSETTS", " MA"),
    (" MICHIGAN", " MI"),
    (" MINNESOTA", " MN"),
    (" MISSISSIPPI", " MS"),
    (" MISSOURI", " MO"),
    (" MONTANA", " MT"),
    (" NEBRASKA", " NE"),
    (" NEVADA", " NV"),
    (" NEW HAMPSHIRE", " NH"),
    (" NEW JERSEY", " NJ"),
    (" NEW MEXICO", " NM"),
    (" NEW YORK", " NY"),
    (" NORTH CAROLINA", " NC"),
    (" NORTH DAKOTA", " ND"),
    (" OHIO", " OH"),
    (" OKLAHOMA", " OK"),
    (" OREGON", " OR"),
    (" PENNSYLVANIA", " PA"),
    (" RHODE ISLAND", " RI"),
    (" SOUTH CAROLINA", " SC"),
    (" SOUTH DAKOTA", " SD"),
    (" TENNESSEE", " TN"),
    (" TEXAS", " TX"),
    (" UTAH", " UT"),
    (" VERMONT", " VT"),
    (" VIRGINIA", " VA"),
    (" WASHINGTON", " WA"),
    (" WEST VIRGINIA", " WV"),
    (" WISCONSIN", " WI"),
    (" WYOMING", " WY"),
)


_WHITESPACE_PATTERN = re.compile(r"\s+")
_NON_ALPHANUM_PATTERN = re.compile(r"[^A-Z0-9]")


def normalize_address(address: str | None) -> str:
    """Return a canonical uppercase, punctuation-free representation of an address."""

    if not address:
        return ""

    working = address.upper()
    working = _apply_replacements(working, _STATE_REPLACEMENTS)
    working = _apply_replacements(working, _COMMON_REPLACEMENTS)
    working = _NON_ALPHANUM_PATTERN.sub(" ", working)
    working = _WHITESPACE_PATTERN.sub(" ", working)
    return working.strip()
