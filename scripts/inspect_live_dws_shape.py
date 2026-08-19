"""Inspect live Nutrient DWS JSON shape without emitting extracted document text.

This diagnostic is intentionally schema-only: object keys, list lengths, and scalar
Python/JSON types. It never prints the API key or string values returned by DWS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from releaseproof.dws import NutrientDwsTransport


def schema_only(value: Any, *, depth: int = 0, max_depth: int = 6) -> Any:
    if depth >= max_depth:
        return {"type": type(value).__name__}
    if isinstance(value, dict):
        return {
            "type": "object",
            "keys": {
                str(key): schema_only(child, depth=depth + 1, max_depth=max_depth)
                for key, child in sorted(value.items(), key=lambda item: str(item[0]))
            },
        }
    if isinstance(value, list):
        return {
            "type": "array",
            "length": len(value),
            "first": schema_only(value[0], depth=depth + 1, max_depth=max_depth) if value else None,
        }
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string", "length": len(value)}
    return {"type": type(value).__name__}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--document", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = NutrientDwsTransport.from_env().build_json_content(args.document)
    report = {
        "execution": "LIVE_NUTRIENT_DWS_SCHEMA_ONLY",
        "document_name": args.document.name,
        "schema": schema_only(payload),
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
