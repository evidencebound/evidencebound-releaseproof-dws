from dataclasses import replace

import pytest

from releaseproof.demo import load_demo_documents
from releaseproof.dws import normalize_fixture
from releaseproof.engine import build_manifest, differential_reverify, review_finding
from releaseproof.model import (
    EvidenceEquivalencePolicy,
    EvidenceIdentity,
    PageDigest,
    ReleaseState,
    evidence_identity_equivalent,
    normalize_evidence_value,
)


def test_normalized_evidence_value_collapses_representation_noise_without_case_guessing():
    assert normalize_evidence_value("  Shipment   ABC-42  ") == "Shipment ABC-42"
    assert normalize_evidence_value("abc-42") != normalize_evidence_value("ABC-42")


def test_bbox_tolerance_is_semantic_equivalence_not_hash_equality():
    old = EvidenceIdentity("invoice", 2, "shipment_id", "S-42", (100.0, 20.0, 160.0, 30.0))
    near = EvidenceIdentity("invoice", 2, "shipment_id", "S-42", (101.0, 19.5, 160.8, 30.5))
    far = EvidenceIdentity("invoice", 2, "shipment_id", "S-42", (104.0, 20.0, 160.0, 30.0))
    assert evidence_identity_equivalent(old, near, bbox_tolerance=2.0)
    assert not evidence_identity_equivalent(old, far, bbox_tolerance=2.0)


def _mismatch_docs(invoice_quantity: str, *, invoice_bytes: bytes = b"invoice"):
    base = {
        "shipment_id": "S-42",
        "currency": "USD",
        "declared_value": "1000",
    }
    invoice_fields = [
        {"field": key, "value": value, "label": key, "confidence": 0.99, "page": 1, "bounds": [10, 10, 30, 20]}
        for key, value in base.items()
    ] + [
        {"field": "quantity", "value": invoice_quantity, "label": "quantity", "confidence": 0.99, "page": 2, "bounds": [100, 20, 160, 30]}
    ]
    shipping_fields = [
        {"field": key, "value": value, "label": key, "confidence": 0.99, "page": 1, "bounds": [10, 10, 30, 20]}
        for key, value in base.items()
    ] + [
        {"field": "quantity", "value": "101", "label": "quantity", "confidence": 0.99, "page": 2, "bounds": [100, 20, 160, 30]}
    ]
    return (
        normalize_fixture("invoice", invoice_bytes, {"fields": invoice_fields}),
        normalize_fixture("shipping", b"shipping", {"fields": shipping_fields}),
    )


def _shift_invoice_quantity_bbox(docs, offset: float):
    invoice = docs[0]
    quantity = invoice.by_field()["quantity"]
    shifted_citation = replace(
        quantity.citation,
        bounds=tuple(x + offset for x in quantity.citation.bounds),
        evidence_slice_sha256=f"bbox-shift-{offset}",
    )
    shifted_fields = tuple(
        replace(field, citation=shifted_citation) if field.field == "quantity" else field
        for field in invoice.fields
    )
    return replace(invoice, document_sha256=f"invoice-shift-{offset}", fields=shifted_fields)


def test_finding_id_is_stable_while_binding_changes_with_material_evidence():
    first = build_manifest(_mismatch_docs("100"))
    second = build_manifest(_mismatch_docs("99", invoice_bytes=b"invoice-v2"))
    a = next(f for f in first.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    b = next(f for f in second.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    assert a.finding_id == b.finding_id
    assert a.binding != b.binding


def test_review_survives_minor_bbox_jitter_but_not_material_bbox_move():
    docs = _mismatch_docs("100")
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    approved = review_finding(initial, finding.finding_id, "reviewer", "APPROVE_EXCEPTION", "checked")

    near_invoice = _shift_invoice_quantity_bbox(docs, 1.0)
    near = differential_reverify(approved, (near_invoice, docs[1]), bbox_tolerance=2.0)
    assert finding.finding_id in near.preserved_review_ids
    assert near.current_manifest.release_state == ReleaseState.VERIFIED

    far_invoice = _shift_invoice_quantity_bbox(docs, 5.0)
    far = differential_reverify(approved, (far_invoice, docs[1]), bbox_tolerance=2.0)
    assert finding.finding_id in far.invalidated_review_ids
    assert far.current_manifest.release_state == ReleaseState.REVIEW_REQUIRED


def test_equivalence_policy_rejects_negative_bbox_tolerance():
    with pytest.raises(ValueError, match="bbox_tolerance"):
        EvidenceEquivalencePolicy(bbox_tolerance=-0.1)


def test_review_freezes_equivalence_policy_and_authority_binding():
    docs = _mismatch_docs("100")
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    policy = EvidenceEquivalencePolicy(bbox_tolerance=2.0)
    approved = review_finding(
        initial,
        finding.finding_id,
        "reviewer",
        "APPROVE_EXCEPTION",
        "checked",
        equivalence_policy=policy,
    )
    review = approved.reviews[0]
    assert review.equivalence_policy == policy
    assert review.authority_binding
    assert approved.unsigned_payload()["reviews"][0]["authority_binding"] == review.authority_binding

    wider = replace(review, equivalence_policy=EvidenceEquivalencePolicy(bbox_tolerance=5.0))
    assert wider.authority_binding != review.authority_binding


def test_old_review_cannot_be_reinterpreted_by_new_runtime_tolerance():
    docs = _mismatch_docs("100")
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    approved = review_finding(
        initial,
        finding.finding_id,
        "reviewer",
        "APPROVE_EXCEPTION",
        "checked under tolerance 2",
        equivalence_policy=EvidenceEquivalencePolicy(bbox_tolerance=2.0),
    )

    moved_invoice = _shift_invoice_quantity_bbox(docs, 4.0)
    # Simulate a future runtime whose default/override is looser. Historical authority
    # must still be evaluated under the policy frozen when the reviewer approved it.
    result = differential_reverify(
        approved,
        (moved_invoice, docs[1]),
        bbox_tolerance=10.0,
    )
    assert finding.finding_id in result.invalidated_review_ids
    assert result.current_manifest.release_state == ReleaseState.REVIEW_REQUIRED


def test_unknown_equivalence_policy_fails_closed():
    docs = _mismatch_docs("100")
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    approved = review_finding(initial, finding.finding_id, "reviewer", "APPROVE_EXCEPTION", "checked")
    review = approved.reviews[0]
    unknown = replace(
        review,
        equivalence_policy=replace(review.equivalence_policy, version="evidence-equivalence/999"),
    )
    rebuilt = build_manifest(docs, (unknown,))
    assert rebuilt.release_state == ReleaseState.REVIEW_REQUIRED


def test_page_7_change_does_not_invalidate_page_2_review():
    docs = _mismatch_docs("100")
    invoice = replace(
        docs[0],
        page_digests=(PageDigest(2, "page-2-same", "canonical-page-pdf"), PageDigest(7, "page-7-old", "canonical-page-pdf")),
    )
    shipping = replace(docs[1], page_digests=(PageDigest(2, "shipping-page-2", "canonical-page-pdf"),))
    initial = build_manifest((invoice, shipping))
    finding = next(f for f in initial.findings if f.rule_id == "CROSS_DOCUMENT_MISMATCH")
    approved = review_finding(initial, finding.finding_id, "reviewer", "APPROVE_EXCEPTION", "checked page 2")

    revised_invoice = replace(
        invoice,
        document_sha256="invoice-v2",
        page_digests=(PageDigest(2, "page-2-same", "canonical-page-pdf"), PageDigest(7, "page-7-new", "canonical-page-pdf")),
    )
    result = differential_reverify(approved, (revised_invoice, shipping))
    assert result.changed_documents == ("invoice",)
    assert result.changed_pages == (("invoice", 7),)
    assert finding.finding_id in result.preserved_review_ids
    assert result.current_manifest.release_state == ReleaseState.VERIFIED


def test_existing_nonmaterial_fixture_still_preserves_review_into_new_manifest():
    docs = load_demo_documents()
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.state == ReleaseState.REVIEW_REQUIRED)
    approved = review_finding(initial, finding.finding_id, "reviewer", "APPROVE_EXCEPTION", "checked")
    result = differential_reverify(approved, load_demo_documents(False, True))
    assert finding.finding_id in result.preserved_review_ids
    assert result.current_manifest.manifest_sha256 != approved.manifest_sha256


def test_reviewed_slice_fixture_changes_semantic_value_not_only_confidence():
    original = load_demo_documents()[0].by_field()["quantity"]
    changed = load_demo_documents(reviewed_invoice_changed=True)[0].by_field()["quantity"]
    assert original.evidence_identity.normalized_value != changed.evidence_identity.normalized_value


def test_confidence_only_drift_does_not_change_semantic_review_identity():
    docs = load_demo_documents()
    initial = build_manifest(docs)
    finding = next(f for f in initial.findings if f.rule_id == "LOW_CONFIDENCE")
    approved = review_finding(initial, finding.finding_id, "reviewer", "APPROVE_EXCEPTION", "checked source")
    invoice = docs[0]
    quantity = invoice.by_field()["quantity"]
    drifted_citation = replace(
        quantity.citation,
        confidence=0.85,
        evidence_slice_sha256="confidence-drift-only",
    )
    drifted_fields = tuple(
        replace(field, citation=drifted_citation) if field.field == "quantity" else field
        for field in invoice.fields
    )
    drifted_invoice = replace(invoice, document_sha256="rescan-sha", fields=drifted_fields)
    result = differential_reverify(approved, (drifted_invoice,) + docs[1:])
    assert finding.finding_id in result.preserved_review_ids
    assert result.invalidated_review_ids == ()
    assert result.current_manifest.release_state == ReleaseState.VERIFIED
