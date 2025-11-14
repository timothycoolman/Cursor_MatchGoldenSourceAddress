# Golden Source Address Matching Service

This repository contains a FastAPI microservice that accepts a free-form US address and attempts to match it against the Pinellas County golden source stored in `PinellasCount_Extract.xlsx`. The service first looks for an exact normalized match and, if none is found, falls back to fuzzy matching powered by [RapidFuzz]. When a match is identified, the response includes the full record from the golden source with column names as JSON keys.

## Features

- Excel-backed golden source loaded once and cached for fast lookups
- Deterministic exact-match detection via aggressive address normalization
- Configurable fuzzy matching threshold using RapidFuzz's `WRatio` scorer
- FastAPI interface suitable for invocation from parent applications or other services
- Health check endpoint for simple monitoring

## Requirements

- Python 3.10+
- System dependencies: none (pure Python stack)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the service

You can start the API using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or via the module shortcut:

```bash
python -m app
```

The service exposes two endpoints:

- `GET /health` – lightweight readiness check
- `POST /match` – performs an address lookup

### Request payload

```json
{
  "address": "1945 Summit Dr, Clearwater, FL 33763"
}
```

### Sample exact-match response

```json
{
  "match_type": "exact_match",
  "confidence": 1.0,
  "input_address": "1945 Summit Dr, Clearwater, FL 33763",
  "normalized_input": "1945 SUMMIT DR CLEARWATER FL 33763",
  "matched_address": "1945 SUMMIT DR CLEARWATER FL 33763",
  "golden_record": {
    "OBJECTID": 322079,
    "Parcel Number": 62916827100000912,
    "Site Address ID": 51252299,
    "Full Address Number": 1945,
    "Street Name": "SUMMIT",
    "Street Type": "DR",
    "Full Address": "1945 SUMMIT DR",
    "Municipality Name": "CLEARWATER",
    "Zipcode": 33763,
    "Status": "Active",
    "Comments": "RESIDENTIAL",
    "GLOBALID": "{CA3AC971-890F-4D93-8793-D193086F4840}",
    "LAST_EDITED_USER": "EGIS",
    "LAST_EDITED_DATE": "9/23/24, 8:57 AM",
    "x": -9210067.101,
    "y": 3247948.055
  }
}
```

Additional columns from the spreadsheet are returned but trimmed here for readability.

When no match qualifies, the API returns `match_type: "no_match"` with `golden_record: null`.

## Configuration

Environment variables allow runtime customization:

- `GOLDEN_SOURCE_PATH` – override the path to the Excel file (defaults to `PinellasCount_Extract.xlsx` in the repo root)
- `FUZZY_MATCH_THRESHOLD` – minimum RapidFuzz score (0–100) required before accepting a fuzzy match (default `92`)
- `DEFAULT_STATE` – fallback state abbreviation appended to records that do not specify one (default `FL`)

## Development notes

- Matching logic lives in `app/matcher.py`
- Address normalization utilities are in `app/normalizer.py`
- API contracts are defined in `app/models.py`

Load tests or CLI experiments can use the matcher directly:

```python
from app.matcher import AddressMatcher
matcher = AddressMatcher()
print(matcher.match("1945 Summit Dr Clearwater FL 33763"))
```

[RapidFuzz]: https://maxbachmann.github.io/RapidFuzz/
