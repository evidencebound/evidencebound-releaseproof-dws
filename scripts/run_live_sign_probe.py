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

import requests

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


def _sanitize_provider_error(response) -> dict[str, object]:
    try:
        payload = response.json()
    except ValueError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        key: payload[key]
        for key in ("details", "requestId", "failingPaths")
        if key in payload
    }


def _sign_with_diagnostics(
    transport: NutrientDwsTransport,
    pdf_bytes: bytes,
    *,
    filename: str,
) -> tuple[bytes | None, int, dict[str, object]]:
    response = requests.post(
        transport.sign_endpoint,
        headers={"Authorization": f"Bearer {transport.api_key}"},
        files={"file": (filename, pdf_bytes, "application/pdf")},
        timeout=transport.timeout_seconds,
    )
    if response.status_code >= 400:
        return None, response.status_code, _sanitize_provider_error(response)
    if not response.content.startswith(b"%PDF-"):
        raise DwsError("DWS signing response was not a PDF")
    return response.content, response.status_code, {}


def run(output_pdf: Path, canonical_output: Path) -> dict[str, object]:
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
    canonical_output.write_bytes(canonical)
    receipt["canonical_pdf_sha256"] = _sha(canonical)
    receipt["canonical_pdf_bytes"] = len(canonical)

    receipt["provider_calls"]["sign"] = 1  # type: ignore[index]
    signed, status_code, provider_error = _sign_with_diagnostics(
        transport,
        canonical,
        filename="releaseproof-sign-probe.pdf",
    )
    if signed is None:
        receipt["signing"] = f"FAIL_HTTP_{status_code}"
        receipt["error_type"] = "DwsError"
        receipt["error"] = f"DWS signing returned HTTP {status_code}"
        if provider_error:
            receipt["provider_error"] = provider_error
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
    parser.add_argument("--canonical-output", type=Path, default=Path("live-sign-probe-canonical.pdf"))
    args = parser.parse_args()

    try:
        receipt = run(args.signed_output, args.canonical_output)
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
