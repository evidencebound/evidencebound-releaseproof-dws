from __future__ import annotations

from dataclasses import replace

from .model import (
    ExtractedDocument,
    Finding,
    HumanReview,
    ReleaseManifest,
    ReleaseState,
    ReverificationResult,
    digest,
    evidence_sets_equivalent,
)


REQUIRED = ("shipment_id", "quantity", "currency", "declared_value")
CONFIDENCE_THRESHOLD = 0.92
DEFAULT_BBOX_TOLERANCE = 2.0


def _finding(
    rule: str,
    field: str,
    severity: str,
    state: ReleaseState,
    message: str,
    citations,
    *,
    scope_document_ids: tuple[str, ...] | None = None,
) -> Finding:
    citations = tuple(citations)
    scope = scope_document_ids or tuple(sorted({citation.document_id for citation in citations}))
    finding_id = digest({
        "finding_schema": "releaseproof/logical-finding/2",
        "rule": rule,
        "field": field,
        "documents": list(scope),
    })[:16]
    return Finding(
        finding_id=finding_id,
        rule_id=rule,
        field=field,
        severity=severity,
        state=state,
        message=message,
        citations=citations,
    )


def reconcile(documents: tuple[ExtractedDocument, ...]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    maps = [(doc, doc.by_field()) for doc in documents]
    all_document_ids = tuple(sorted(doc.document_id for doc in documents))
    for field in REQUIRED:
        values = []
        citations = []
        missing = []
        for doc, mapping in maps:
            if field not in mapping:
                missing.append(doc.document_id)
                continue
            item = mapping[field]
            values.append(item.value)
            citations.append(item.citation)
            if item.citation.confidence < CONFIDENCE_THRESHOLD:
                findings.append(_finding(
                    "LOW_CONFIDENCE",
                    field,
                    "medium",
                    ReleaseState.REVIEW_REQUIRED,
                    f"{doc.document_id}.{field} confidence={item.citation.confidence:.3f} below {CONFIDENCE_THRESHOLD:.2f}",
                    (item.citation,),
                    scope_document_ids=(doc.document_id,),
                ))
        if missing:
            findings.append(_finding(
                "MISSING_FIELD",
                field,
                "high",
                ReleaseState.BLOCKED,
                f"Required field {field} missing from: {', '.join(sorted(missing))}",
                citations,
                scope_document_ids=all_document_ids,
            ))
        elif len(set(values)) > 1:
            findings.append(_finding(
                "CROSS_DOCUMENT_MISMATCH",
                field,
                "high",
                ReleaseState.REVIEW_REQUIRED,
                f"Documents disagree on {field}: {sorted(set(values))}",
                citations,
                scope_document_ids=all_document_ids,
            ))
    return tuple(findings)


def _review_matches_finding(
    review: HumanReview,
    finding: Finding,
    *,
    bbox_tolerance: float = DEFAULT_BBOX_TOLERANCE,
) -> bool:
    if review.finding_id != finding.finding_id:
        return False
    if review.evidence_identities:
        return evidence_sets_equivalent(
            review.evidence_identities,
            finding.evidence_identities,
            bbox_tolerance=bbox_tolerance,
        )
    # Historical manifests created before semantic identity support remain fail-closed
    # to their exact binding. No semantic continuity is inferred retroactively.
    return review.finding_binding == finding.binding


def _valid_reviews(
    findings: tuple[Finding, ...],
    reviews: tuple[HumanReview, ...],
    *,
    bbox_tolerance: float = DEFAULT_BBOX_TOLERANCE,
) -> dict[str, HumanReview]:
    by_id = {review.finding_id: review for review in reviews}
    valid: dict[str, HumanReview] = {}
    for finding in findings:
        review = by_id.get(finding.finding_id)
        if review and _review_matches_finding(review, finding, bbox_tolerance=bbox_tolerance):
            valid[finding.finding_id] = review
    return valid


def decide(
    findings: tuple[Finding, ...],
    reviews: tuple[HumanReview, ...],
    *,
    bbox_tolerance: float = DEFAULT_BBOX_TOLERANCE,
) -> ReleaseState:
    valid = _valid_reviews(findings, reviews, bbox_tolerance=bbox_tolerance)
    if any(f.state == ReleaseState.BLOCKED for f in findings):
        return ReleaseState.BLOCKED
    for finding in findings:
        if finding.state == ReleaseState.REVIEW_REQUIRED:
            review = valid.get(finding.finding_id)
            if review is None:
                return ReleaseState.REVIEW_REQUIRED
            if review.decision != "APPROVE_EXCEPTION":
                return ReleaseState.BLOCKED
    return ReleaseState.VERIFIED


def build_manifest(
    documents: tuple[ExtractedDocument, ...],
    reviews: tuple[HumanReview, ...] = (),
    policy_version: str = "trade-release/1",
    *,
    bbox_tolerance: float = DEFAULT_BBOX_TOLERANCE,
) -> ReleaseManifest:
    findings = reconcile(documents)
    state = decide(findings, reviews, bbox_tolerance=bbox_tolerance)
    manifest = ReleaseManifest("releaseproof/2", policy_version, documents, findings, reviews, state)
    return replace(manifest, manifest_sha256=digest(manifest.unsigned_payload()))


def review_finding(
    manifest: ReleaseManifest,
    finding_id: str,
    reviewer: str,
    decision: str,
    rationale: str,
) -> ReleaseManifest:
    finding = next((item for item in manifest.findings if item.finding_id == finding_id), None)
    if finding is None:
        raise KeyError(finding_id)
    review = HumanReview(
        finding_id=finding.finding_id,
        finding_binding=finding.binding,
        decision=decision,
        reviewer=reviewer,
        rationale=rationale,
        evidence_identities=finding.evidence_identities,
    )
    kept = tuple(item for item in manifest.reviews if item.finding_id != finding_id)
    return build_manifest(manifest.documents, kept + (review,), manifest.policy_version)


def verify_manifest(manifest: ReleaseManifest, current_documents: tuple[ExtractedDocument, ...]) -> ReleaseState:
    if digest(manifest.unsigned_payload()) != manifest.manifest_sha256:
        return ReleaseState.BLOCKED
    expected = {d.document_id: d.document_sha256 for d in manifest.documents}
    current = {d.document_id: d.document_sha256 for d in current_documents}
    if expected != current:
        return ReleaseState.INVALIDATED
    rebuilt = build_manifest(current_documents, manifest.reviews, manifest.policy_version)
    if rebuilt.manifest_sha256 != manifest.manifest_sha256:
        return ReleaseState.INVALIDATED
    return rebuilt.release_state


def _changed_pages(
    prior_documents: tuple[ExtractedDocument, ...],
    current_documents: tuple[ExtractedDocument, ...],
) -> tuple[tuple[str, int], ...]:
    prior_by_id = {document.document_id: document for document in prior_documents}
    current_by_id = {document.document_id: document for document in current_documents}
    changed: list[tuple[str, int]] = []
    for document_id in sorted(set(prior_by_id) | set(current_by_id)):
        old_document = prior_by_id.get(document_id)
        new_document = current_by_id.get(document_id)
        old_pages = old_document.page_digest_map() if old_document else {}
        new_pages = new_document.page_digest_map() if new_document else {}
        for page in sorted(set(old_pages) | set(new_pages)):
            if old_pages.get(page) != new_pages.get(page):
                changed.append((document_id, page))
    return tuple(changed)


def differential_reverify(
    prior: ReleaseManifest,
    current_documents: tuple[ExtractedDocument, ...],
    *,
    bbox_tolerance: float = DEFAULT_BBOX_TOLERANCE,
) -> ReverificationResult:
    """Mint a current manifest while reusing only still-valid semantic review authority.

    Whole-document changes never make the old manifest current. A fresh manifest is
    always minted. Reviews are carried forward only when the same logical finding is
    reproduced from an equivalent normalized evidence set.
    """
    if digest(prior.unsigned_payload()) != prior.manifest_sha256:
        raise ValueError("prior manifest integrity failure")
    old_docs = {d.document_id: d.document_sha256 for d in prior.documents}
    new_docs = {d.document_id: d.document_sha256 for d in current_documents}
    changed_documents = tuple(sorted(
        doc_id for doc_id in set(old_docs) | set(new_docs)
        if old_docs.get(doc_id) != new_docs.get(doc_id)
    ))
    changed_pages = _changed_pages(prior.documents, current_documents)
    current_findings = reconcile(current_documents)
    current_by_id = {f.finding_id: f for f in current_findings}
    preserved: list[HumanReview] = []
    invalidated: list[HumanReview] = []
    for review in prior.reviews:
        finding = current_by_id.get(review.finding_id)
        if finding is not None and _review_matches_finding(
            review,
            finding,
            bbox_tolerance=bbox_tolerance,
        ):
            preserved.append(review)
        else:
            invalidated.append(review)
    current = build_manifest(
        current_documents,
        tuple(preserved),
        prior.policy_version,
        bbox_tolerance=bbox_tolerance,
    )
    return ReverificationResult(
        prior_manifest_sha256=prior.manifest_sha256,
        current_manifest=current,
        changed_documents=changed_documents,
        preserved_review_ids=tuple(sorted(r.finding_id for r in preserved)),
        invalidated_review_ids=tuple(sorted(r.finding_id for r in invalidated)),
        changed_pages=changed_pages,
    )
