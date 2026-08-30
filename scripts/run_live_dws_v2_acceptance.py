"""Run one quota-bounded hosted acceptance of the DWS-native ReleaseProof v2 path.

Only synthetic documents are sent to Nutrient. Processor and Data Extraction use
separate product credentials. The receipt excludes API keys and raw provider payloads.
On provider-contract failure it retains only a structural shape diagnostic.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from generate_synthetic_trade_pdfs import PACKET, _pdf_bytes
from releaseproof.dws import (
    NutrientDataExtractionTransport,
    NutrientDwsTransport,
    process_with_native_dws,
)
from releaseproof.engine import build_manifest, differential_reverify, review_finding
from releaseproof.model import (
    COORDINATE_SPACE_NUTRIENT_PROCESSOR_CANONICAL,
    ReleaseState,
)


SCHEMA = {
    "type": "object",
    "properties": {
        "shipment_id": {"type": "string", "description": "Shipment ID"},
        "quantity": {"type": "string", "description": "Quantity"},
        "currency": {"type": "string", "description": "Currency"},
        "declared_value": {"type": "string", "description": "Declared Value"},
    },
    "required": ["shipment_id", "quantity", "currency", "declared_value"],
}
SCHEMA_SOURCE = "acceptance-test-schema:not-studio-generated"
TARGET_FIELD = "shipment_id"
TARGET_RULE = "CROSS_DOCUMENT_MISMATCH"


def _shape(value: Any, *, depth: int = 0) -> Any:
    """Return provider response structure only, never extracted scalar values."""
    if depth >= 5:
        return type(value).__name__
    if isinstance(value, dict):
        return {str(key): _shape(item, depth=depth + 1) for key, item in value.items()}
    if isinstance(value, list):
        return {
            "type": "array",
            "length": len(value),
            "first": _shape(value[0], depth=depth + 1) if value else None,
        }
    return type(value).__name__


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _live_product_keys() -> tuple[str, str]:
    """Fail closed before network calls unless both Nutrient product keys exist."""
    processor_key = os.environ.get("NUTRIENT_API_KEY")
    if not processor_key:
        raise RuntimeError("NUTRIENT_API_KEY is required for Processor")
    extraction_key = os.environ.get("NUTRIENT_DATA_EXTRACTION_API_KEY")
    if not extraction_key:
        raise RuntimeError(
            "NUTRIENT_DATA_EXTRACTION_API_KEY is required for Data Extraction"
        )
    return processor_key, extraction_key


def _with_shipment(lines: list[str], shipment_id: str) -> list[str]:
    return [
        f"Shipment ID: {shipment_id}" if line.startswith("Shipment ID:") else line
        for line in lines
    ]


def _write_pdf(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _pdf_bytes(lines)
    if not data.startswith(b"%PDF-") or not data.rstrip().endswith(b"%%EOF"):
        raise RuntimeError(f"invalid generated PDF envelope: {path.name}")
    path.write_bytes(data)


def _write_nonmaterial_revision(source: Path, target: Path) -> None:
    data = source.read_bytes()
    marker = b"%%EOF\n"
    if not data.endswith(marker):
        raise RuntimeError("base invoice PDF does not end with expected EOF marker")
    revised = data[:-len(marker)] + b"% ReleaseProof hosted-v2 nonmaterial revision\n" + marker
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(revised)
    if _sha(revised) == _sha(data):
        raise RuntimeError("nonmaterial revision did not change source bytes")


class CountingProcessor:
    def __init__(self, api_key: str) -> None:
        self.inner = NutrientDwsTransport(api_key)
        self.calls = {"canonicalize": 0, "isolate_page": 0, "sign": 0}

    def canonicalize_pdf(self, path: Path) -> bytes:
        self.calls["canonicalize"] += 1
        return self.inner.canonicalize_pdf(path)

    def isolate_page(self, canonical_pdf: bytes, *, page: int) -> bytes:
        self.calls["isolate_page"] += 1
        return self.inner.isolate_page(canonical_pdf, page=page)

    def sign_pdf(self, pdf_bytes: bytes, *, filename: str = "release.pdf") -> bytes:
        self.calls["sign"] += 1
        return self.inner.sign_pdf(pdf_bytes, filename=filename)


class RecordingExtraction:
    def __init__(self, api_key: str) -> None:
        self.inner = NutrientDataExtractionTransport(api_key)
        self.calls = 0
        self.last_payload: dict[str, Any] | None = None

    def extract_pdf(
        self,
        pdf_bytes: bytes,
        *,
        filename: str,
        schema: dict[str, Any],
        mode: str,
    ) -> dict[str, Any]:
        self.calls += 1
        payload = self.inner.extract_pdf(
            pdf_bytes,
            filename=filename,
            schema=schema,
            mode=mode,
        )
        self.last_payload = payload
        return payload


def _validate_native_document(document) -> dict[str, Any]:
    if document.dws_operation != "nutrient-data-extraction:/extraction/extract":
        raise RuntimeError(f"unexpected DWS operation: {document.dws_operation}")
    if not document.fields:
        raise RuntimeError(f"{document.document_id}: no grounded fields")
    page_hashes = {item.page: item.sha256 for item in document.page_digests}
    if not page_hashes:
        raise RuntimeError(f"{document.document_id}: no canonical page hashes")
    for field in document.fields:
        citation = field.citation
        if citation.page_hash_source != "canonical-page-pdf" or not citation.page_sha256:
            raise RuntimeError(f"{document.document_id}.{field.field}: canonical page hash missing")
        if citation.coordinate_space != COORDINATE_SPACE_NUTRIENT_PROCESSOR_CANONICAL:
            raise RuntimeError(
                f"{document.document_id}.{field.field}: non-canonical coordinate space"
            )
        if not citation.source_evidence:
            raise RuntimeError(f"{document.document_id}.{field.field}: source evidence missing")
        if not 0.0 <= citation.confidence <= 1.0:
            raise RuntimeError(f"{document.document_id}.{field.field}: confidence invalid")
    return {
        "document_id": document.document_id,
        "field_count": len(document.fields),
        "page_count": len(document.page_digests),
        "processor_or_extraction_receipt_sha256": document.dws_receipt_sha256,
        "coordinate_spaces": sorted({field.citation.coordinate_space for field in document.fields}),
        "page_hash_sources": sorted({field.citation.page_hash_source for field in document.fields}),
    }


def _process(document_id: str, path: Path, processor, extraction):
    return process_with_native_dws(
        document_id,
        path,
        processor,
        extraction,
        schema=SCHEMA,
        schema_source=SCHEMA_SOURCE,
        mode="structure",
    )


def _find_target(manifest):
    return next(
        (
            finding
            for finding in manifest.findings
            if finding.rule_id == TARGET_RULE and finding.field == TARGET_FIELD
        ),
        None,
    )


def _review_all_review_required(manifest):
    reviewed = manifest
    for finding in manifest.findings:
        if finding.state == ReleaseState.REVIEW_REQUIRED:
            reviewed = review_finding(
                reviewed,
                finding.finding_id,
                reviewer="releaseproof-hosted-v2-acceptance-harness",
                decision="APPROVE_EXCEPTION",
                rationale=(
                    "Synthetic acceptance-harness review. Not a real reviewer metric or "
                    "customer approval. Used only to test authority continuity."
                ),
            )
    return reviewed


def run(workdir: Path, signed_output: Path) -> dict[str, Any]:
    processor_key, extraction_key = _live_product_keys()
    processor = CountingProcessor(processor_key)
    extraction = RecordingExtraction(extraction_key)
    receipt: dict[str, Any] = {
        "execution": "LIVE_NUTRIENT_DWS_V2",
        "status": "FAIL",
        "schema_source": SCHEMA_SOURCE,
        "mode": "structure",
        "synthetic_documents_only": True,
        "credential_classes": {
            "processor": "NUTRIENT_API_KEY",
            "data_extraction": "NUTRIENT_DATA_EXTRACTION_API_KEY",
        },
    }

    try:
        base = workdir / "baseline"
        _write_pdf(base / "invoice.pdf", PACKET["invoice.pdf"])
        _write_pdf(base / "shipping.pdf", PACKET["shipping.pdf"])
        _write_pdf(
            base / "certificate.pdf",
            _with_shipment(PACKET["certificate.pdf"], "SHP-260818-43"),
        )

        baseline_documents = tuple(
            _process(document_id, base / filename, processor, extraction)
            for document_id, filename in (
                ("invoice", "invoice.pdf"),
                ("shipping", "shipping.pdf"),
                ("certificate", "certificate.pdf"),
            )
        )
        receipt["baseline_documents"] = [
            _validate_native_document(document) for document in baseline_documents
        ]

        baseline = build_manifest(baseline_documents)
        if baseline.release_state == ReleaseState.BLOCKED:
            raise RuntimeError("baseline packet is BLOCKED; hosted extraction missed required fields")
        target = _find_target(baseline)
        if target is None:
            raise RuntimeError("intentional hosted shipment mismatch was not reproduced")

        reviewed = _review_all_review_required(baseline)
        if reviewed.release_state != ReleaseState.VERIFIED:
            raise RuntimeError(
                f"synthetic reviewed baseline did not reach VERIFIED: {reviewed.release_state.value}"
            )
        target_review = next(
            review for review in reviewed.reviews if review.finding_id == target.finding_id
        )

        nonmaterial_path = workdir / "revisions" / "invoice-nonmaterial.pdf"
        _write_nonmaterial_revision(base / "invoice.pdf", nonmaterial_path)
        nonmaterial_invoice = _process("invoice", nonmaterial_path, processor, extraction)
        _validate_native_document(nonmaterial_invoice)
        nonmaterial = differential_reverify(
            reviewed,
            (nonmaterial_invoice, baseline_documents[1], baseline_documents[2]),
        )
        if target.finding_id not in nonmaterial.preserved_review_ids:
            raise RuntimeError("target review was not preserved after non-material source revision")
        if nonmaterial.current_manifest.release_state != ReleaseState.VERIFIED:
            raise RuntimeError(
                "non-material revision did not remain VERIFIED after semantic reverification"
            )

        material_path = workdir / "revisions" / "invoice-material.pdf"
        _write_pdf(
            material_path,
            _with_shipment(PACKET["invoice.pdf"], "SHP-260818-43"),
        )
        material_invoice = _process("invoice", material_path, processor, extraction)
        _validate_native_document(material_invoice)
        material = differential_reverify(
            reviewed,
            (material_invoice, baseline_documents[1], baseline_documents[2]),
        )
        if target.finding_id not in material.invalidated_review_ids:
            raise RuntimeError("target review was not invalidated after material evidence change")
        if material.current_manifest.release_state != ReleaseState.REVIEW_REQUIRED:
            raise RuntimeError("material evidence change did not return packet to REVIEW_REQUIRED")

        release_pdf = _pdf_bytes(
            [
                "RELEASEPROOF VERIFIED RELEASE ATTESTATION",
                f"Manifest: {nonmaterial.current_manifest.manifest_sha256}",
                f"State: {nonmaterial.current_manifest.release_state.value}",
                f"Authority: {target_review.authority_binding}",
            ]
        )
        signed = processor.sign_pdf(release_pdf, filename="releaseproof-verified-release.pdf")
        signed_output.parent.mkdir(parents=True, exist_ok=True)
        signed_output.write_bytes(signed)

        receipt.update(
            {
                "status": "PASS",
                "baseline": {
                    "initial_state": baseline.release_state.value,
                    "reviewed_state": reviewed.release_state.value,
                    "manifest_sha256": reviewed.manifest_sha256,
                    "target_finding_id": target.finding_id,
                    "target_authority_binding": target_review.authority_binding,
                    "review_count": len(reviewed.reviews),
                },
                "nonmaterial_revision": {
                    "source_bytes_changed": _sha((base / "invoice.pdf").read_bytes())
                    != _sha(nonmaterial_path.read_bytes()),
                    "current_state": nonmaterial.current_manifest.release_state.value,
                    "current_manifest_sha256": nonmaterial.current_manifest.manifest_sha256,
                    "target_review_preserved": target.finding_id
                    in nonmaterial.preserved_review_ids,
                    "changed_documents": list(nonmaterial.changed_documents),
                    "changed_pages": [list(item) for item in nonmaterial.changed_pages],
                },
                "material_revision": {
                    "source_bytes_changed": _sha((base / "invoice.pdf").read_bytes())
                    != _sha(material_path.read_bytes()),
                    "current_state": material.current_manifest.release_state.value,
                    "current_manifest_sha256": material.current_manifest.manifest_sha256,
                    "target_review_invalidated": target.finding_id
                    in material.invalidated_review_ids,
                    "changed_documents": list(material.changed_documents),
                    "changed_pages": [list(item) for item in material.changed_pages],
                },
                "signed_release": {
                    "source_manifest_sha256": nonmaterial.current_manifest.manifest_sha256,
                    "signed_pdf_sha256": _sha(signed),
                    "signed_pdf_bytes": len(signed),
                },
            }
        )
    except Exception as exc:
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
        if extraction.last_payload is not None:
            receipt["last_data_extraction_response_shape"] = _shape(extraction.last_payload)
        raise
    finally:
        receipt["provider_calls"] = {
            "processor": dict(processor.calls),
            "data_extraction": extraction.calls,
        }
        run.last_receipt = receipt

    return receipt


run.last_receipt = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, default=Path("live-dws-v2-work"))
    parser.add_argument("--output", type=Path, default=Path("live-dws-v2-receipt.json"))
    parser.add_argument(
        "--signed-output",
        type=Path,
        default=Path("live-dws-v2-signed-release.pdf"),
    )
    args = parser.parse_args()

    try:
        receipt = run(args.workdir, args.signed_output)
        exit_code = 0
    except Exception:
        receipt = run.last_receipt or {
            "execution": "LIVE_NUTRIENT_DWS_V2",
            "status": "FAIL",
            "error": {
                "type": "UNKNOWN",
                "message": "acceptance failed before receipt initialization",
            },
        }
        exit_code = 1

    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
