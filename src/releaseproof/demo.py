from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .dws import normalize_fixture
from .engine import build_manifest, differential_reverify, review_finding, verify_manifest
from .model import ExtractedDocument

ROOT = Path(__file__).resolve().parents[2]


def load_demo_documents(
    changed_shipping: bool = False,
    nonmaterial_invoice: bool = False,
    reviewed_invoice_changed: bool = False,
) -> tuple[ExtractedDocument, ...]:
    if reviewed_invoice_changed:
        invoice_name = "invoice_review_changed"
    else:
        invoice_name = "invoice_nonmaterial" if nonmaterial_invoice else "invoice"
    names = [invoice_name, "shipping_changed" if changed_shipping else "shipping", "certificate"]
    docs = []
    for name in names:
        payload = json.loads((ROOT / "fixtures" / f"{name}.json").read_text())
        raw = (ROOT / "fixtures" / f"{name}.txt").read_bytes()
        logical_id = (
            "shipping" if name == "shipping_changed"
            else "invoice" if name in {"invoice_nonmaterial", "invoice_review_changed"}
            else name
        )
        docs.append(normalize_fixture(logical_id, raw, payload))
    return tuple(docs)


def run_demo() -> dict:
    docs = load_demo_documents(False)
    initial = build_manifest(docs)
    manifest = initial
    for finding in initial.findings:
        if finding.state.value == "REVIEW_REQUIRED":
            manifest = review_finding(manifest, finding.finding_id, "demo-reviewer", "APPROVE_EXCEPTION", "Controlled exception accepted for demo")
    verified = verify_manifest(manifest, docs)
    nonmaterial = load_demo_documents(False, True)
    nonmaterial_reverification = differential_reverify(manifest, nonmaterial)
    changed = load_demo_documents(True)
    material_reverification = differential_reverify(manifest, changed)
    reviewed_slice_changed = load_demo_documents(reviewed_invoice_changed=True)
    reviewed_slice_reverification = differential_reverify(manifest, reviewed_slice_changed)
    after_change = verify_manifest(manifest, changed)
    return {
        "initial_state": initial.release_state.value,
        "reviewed_state": manifest.release_state.value,
        "verification": verified.value,
        "after_source_change": after_change.value,
        "nonmaterial_revision": {
            "changed_documents": list(nonmaterial_reverification.changed_documents),
            "preserved_review_ids": list(nonmaterial_reverification.preserved_review_ids),
            "invalidated_review_ids": list(nonmaterial_reverification.invalidated_review_ids),
            "current_state": nonmaterial_reverification.current_manifest.release_state.value,
        },
        "material_revision": {
            "changed_documents": list(material_reverification.changed_documents),
            "preserved_review_ids": list(material_reverification.preserved_review_ids),
            "invalidated_review_ids": list(material_reverification.invalidated_review_ids),
            "current_state": material_reverification.current_manifest.release_state.value,
        },
        "reviewed_slice_revision": {
            "changed_documents": list(reviewed_slice_reverification.changed_documents),
            "preserved_review_ids": list(reviewed_slice_reverification.preserved_review_ids),
            "invalidated_review_ids": list(reviewed_slice_reverification.invalidated_review_ids),
            "current_state": reviewed_slice_reverification.current_manifest.release_state.value,
        },
        "findings": [asdict(f) for f in initial.findings],
        "manifest_sha256": manifest.manifest_sha256,
    }
