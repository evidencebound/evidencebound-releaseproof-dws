"""Run Differential Reverification over hosted Nutrient DWS output.

The review decision in this script is a synthetic acceptance-harness decision over
non-sensitive generated documents. It verifies binding/reuse mechanics only and is
not represented as a real human-review metric.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from releaseproof.dws import NutrientDwsTransport, process_with_dws
from releaseproof.engine import build_manifest, differential_reverify, review_finding
from releaseproof.model import ReleaseState

from generate_synthetic_revision import main as generate_revision


ALIASES = {
    "shipment id": "shipment_id",
    "shipment_id": "shipment_id",
    "quantity": "quantity",
    "qty": "quantity",
    "currency": "currency",
    "declared value": "declared_value",
    "declared_value": "declared_value",
}


def _process(transport: NutrientDwsTransport, invoice: Path):
    return tuple(
        process_with_dws(doc_id, path, transport, field_aliases=ALIASES)
        for doc_id, path in (
            ("invoice", invoice),
            ("shipping", Path("live-probe-input/shipping.pdf")),
            ("certificate", Path("live-probe-input/certificate.pdf")),
        )
    )


def main() -> int:
    generate_revision()
    transport = NutrientDwsTransport.from_env()
    original_docs = _process(transport, Path("live-probe-input/invoice.pdf"))
    original = build_manifest(original_docs)
    reviewable = next(
        (f for f in original.findings if f.state == ReleaseState.REVIEW_REQUIRED),
        None,
    )
    if reviewable is None:
        raise RuntimeError("live packet produced no REVIEW_REQUIRED finding for binding test")
    approved = review_finding(
        original,
        reviewable.finding_id,
        reviewer="synthetic-live-acceptance",
        decision="APPROVE_EXCEPTION",
        rationale="Synthetic acceptance-harness decision; verifies binding mechanics only.",
    )

    revised_docs = _process(transport, Path("live-probe-revision/invoice-revised.pdf"))
    result = differential_reverify(approved, revised_docs)
    original_invoice = next(d for d in original_docs if d.document_id == "invoice")
    revised_invoice = next(d for d in revised_docs if d.document_id == "invoice")

    output = {
        "execution": "LIVE_NUTRIENT_DWS_DIFFERENTIAL_REVERIFICATION",
        "review_evidence_class": "synthetic-acceptance-harness-not-human-metric",
        "original_manifest_sha256": original.manifest_sha256,
        "approved_manifest_sha256": approved.manifest_sha256,
        "current_manifest_sha256": result.current_manifest.manifest_sha256,
        "original_state": original.release_state.value,
        "approved_state": approved.release_state.value,
        "current_state": result.current_manifest.release_state.value,
        "original_invoice_sha256": original_invoice.document_sha256,
        "revised_invoice_sha256": revised_invoice.document_sha256,
        "invoice_bytes_changed": original_invoice.document_sha256 != revised_invoice.document_sha256,
        "changed_documents": list(result.changed_documents),
        "preserved_review_ids": list(result.preserved_review_ids),
        "invalidated_review_ids": list(result.invalidated_review_ids),
        "reviewed_finding": asdict(reviewable),
        "current_findings": [asdict(f) for f in result.current_manifest.findings],
        "documents": [
            {
                "document_id": d.document_id,
                "document_sha256": d.document_sha256,
                "dws_operation": d.dws_operation,
                "dws_receipt_sha256": d.dws_receipt_sha256,
                "field_evidence_slices": {
                    f.field: f.citation.evidence_slice_sha256 for f in d.fields
                },
            }
            for d in revised_docs
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
