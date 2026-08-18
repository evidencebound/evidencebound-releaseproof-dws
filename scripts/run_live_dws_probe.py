from __future__ import annotations
from dataclasses import asdict
import argparse
import json
from pathlib import Path

from releaseproof.dws import NutrientDwsTransport, process_with_dws
from releaseproof.engine import build_manifest

ALIASES = {
    "shipment id": "shipment_id",
    "shipment_id": "shipment_id",
    "quantity": "quantity",
    "qty": "quantity",
    "currency": "currency",
    "declared value": "declared_value",
    "declared_value": "declared_value",
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--invoice", required=True, type=Path)
    parser.add_argument("--shipping", required=True, type=Path)
    parser.add_argument("--certificate", required=True, type=Path)
    args = parser.parse_args()
    transport = NutrientDwsTransport.from_env()
    docs = tuple(
        process_with_dws(doc_id, path, transport, field_aliases=ALIASES)
        for doc_id, path in (
            ("invoice", args.invoice),
            ("shipping", args.shipping),
            ("certificate", args.certificate),
        )
    )
    manifest = build_manifest(docs)
    print(json.dumps({
        "execution": "LIVE_NUTRIENT_DWS",
        "release_state": manifest.release_state.value,
        "documents": [asdict(d) for d in docs],
        "findings": [asdict(f) for f in manifest.findings],
        "manifest_sha256": manifest.manifest_sha256,
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
