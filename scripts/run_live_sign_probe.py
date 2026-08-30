"""Probe Nutrient /sign with a Processor-normalized synthetic PDF.

This probe is intentionally independent of Data Extraction. It uses only synthetic
content, never prints credentials or raw provider error bodies, and distinguishes
Processor normalization from the optional Digital Signature endpoint.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path

from generate_synthetic_trade_pdfs import _pdf_bytes
from releaseproof.dws import DwsError, NutrientDwsTransport


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _status_from_error(exc: DwsError) -> str:
    text = str(exc)
    if "HTTP " in text:
        code = text.rsplit("HTTP ", 1)[-1].strip()
        if code.isdigit():
            return f"FAIL_HTTP_{code}"
    return "FAIL"


def run(output_pdf: Path) -> dict[str, object]:
    key = os.environ.get("NUTRIENT_API_KEY")
    if not key:
        raise RuntimeError("NUTRIENT_API_KEY is required")

    transport = NutrientDwsTransport(key)
    source = Path("live-sign-probe-source.pdf")
    source.write_bytes(
        _pdf_bytes(
            [
                "RELEASEPROOF SIGNING PROBE",
                "Synthetic document only",
                "Purpose: verify optional Nutrient /sign transport",
            ]
        )
    )

    receipt: dict[str, object] = {
        "execution": "LIVE_NUTRIENT_SIGN_PROBE",
        "synthetic_document_only": True,
        "processor_normalization": "UNRUN",
        "signing": "UNRUN",
        "provider_calls": {"canonicalize": 0, "sign": 0},
    }

    canonical = transport.canonicalize_pdf(source)
    receipt["provider_calls"]["canonicalize"] = 1  # type: ignore[index]
    receipt["processor_normalization"] = "PASS"
    receipt["canonical_pdf_sha256"] = _sha(canonical)
    receipt["canonical_pdf_bytes"] = len(canonical)

    receipt["provider_calls"]["sign"] = 1  # type: ignore[index]
    try:
        signed = transport.sign_pdf(canonical, filename="releaseproof-sign-probe.pdf")
    except DwsError as exc:
        receipt["signing"] = _status_from_error(exc)
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)
        return receipt

    output_pdf.write_bytes(signed)
    receipt["signing"] = "PASS"
    receipt["signed_pdf_sha256"] = _sha(signed)
    receipt["signed_pdf_bytes"] = len(signed)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=Path("live-sign-probe-receipt.json"))
    parser.add_argument("--signed-output", type=Path, default=Path("live-sign-probe-signed.pdf"))
    args = parser.parse_args()

    try:
        receipt = run(args.signed_output)
    except Exception as exc:
        receipt = {
            "execution": "LIVE_NUTRIENT_SIGN_PROBE",
            "signing": "FAIL_PRECONDITION",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("signing") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
