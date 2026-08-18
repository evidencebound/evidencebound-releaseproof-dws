from __future__ import annotations

from dataclasses import replace

from .model import ExtractedDocument, Finding, HumanReview, ReleaseManifest, ReleaseState, digest


REQUIRED = ("shipment_id", "quantity", "currency", "declared_value")
CONFIDENCE_THRESHOLD = 0.92


def _finding(rule: str, field: str, severity: str, state: ReleaseState, message: str, citations) -> Finding:
    return Finding(
        finding_id=digest({"rule": rule, "field": field, "evidence_slices": [c.evidence_slice_sha256 for c in citations]})[:16],
        rule_id=rule,
        field=field,
        severity=severity,
        state=state,
        message=message,
        citations=tuple(citations),
    )


def reconcile(documents: tuple[ExtractedDocument, ...]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    maps = [(doc, doc.by_field()) for doc in documents]
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
                    "LOW_CONFIDENCE", field, "medium", ReleaseState.REVIEW_REQUIRED,
                    f"{doc.document_id}.{field} confidence={item.citation.confidence:.3f} below {CONFIDENCE_THRESHOLD:.2f}",
                    (item.citation,),
                ))
        if missing:
            findings.append(_finding(
                "MISSING_FIELD", field, "high", ReleaseState.BLOCKED,
                f"Required field {field} missing from: {', '.join(sorted(missing))}", citations,
            ))
        elif len(set(values)) > 1:
            findings.append(_finding(
                "CROSS_DOCUMENT_MISMATCH", field, "high", ReleaseState.REVIEW_REQUIRED,
                f"Documents disagree on {field}: {sorted(set(values))}", citations,
            ))
    return tuple(findings)


def _valid_reviews(findings: tuple[Finding, ...], reviews: tuple[HumanReview, ...]) -> dict[str, HumanReview]:
    by_id = {review.finding_id: review for review in reviews}
    valid: dict[str, HumanReview] = {}
    for finding in findings:
        review = by_id.get(finding.finding_id)
        if review and review.finding_binding == finding.binding:
            valid[finding.finding_id] = review
    return valid


def decide(findings: tuple[Finding, ...], reviews: tuple[HumanReview, ...]) -> ReleaseState:
    valid = _valid_reviews(findings, reviews)
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
) -> ReleaseManifest:
    findings = reconcile(documents)
    state = decide(findings, reviews)
    manifest = ReleaseManifest("releaseproof/1", policy_version, documents, findings, reviews, state)
    return replace(manifest, manifest_sha256=digest(manifest.unsigned_payload()))


def review_finding(manifest: ReleaseManifest, finding_id: str, reviewer: str, decision: str, rationale: str) -> ReleaseManifest:
    finding = next((item for item in manifest.findings if item.finding_id == finding_id), None)
    if finding is None:
        raise KeyError(finding_id)
    review = HumanReview(finding.finding_id, finding.binding, decision, reviewer, rationale)
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


def differential_reverify(
    prior: ReleaseManifest,
    current_documents: tuple[ExtractedDocument, ...],
):
    """Mint a current manifest while reusing only still-valid evidence-scoped reviews.

    Whole-document changes never make the old manifest current. Instead this function
    computes a fresh manifest and carries forward only reviews whose finding binding
    is reproduced from the current source-grounded evidence slices.
    """
    from .model import ReverificationResult

    if digest(prior.unsigned_payload()) != prior.manifest_sha256:
        raise ValueError("prior manifest integrity failure")
    old_docs = {d.document_id: d.document_sha256 for d in prior.documents}
    new_docs = {d.document_id: d.document_sha256 for d in current_documents}
    changed_documents = tuple(sorted(
        doc_id for doc_id in set(old_docs) | set(new_docs)
        if old_docs.get(doc_id) != new_docs.get(doc_id)
    ))
    current_findings = reconcile(current_documents)
    current_by_id = {f.finding_id: f for f in current_findings}
    preserved = []
    invalidated = []
    for review in prior.reviews:
        finding = current_by_id.get(review.finding_id)
        if finding is not None and finding.binding == review.finding_binding:
            preserved.append(review)
        else:
            invalidated.append(review)
    current = build_manifest(current_documents, tuple(preserved), prior.policy_version)
    return ReverificationResult(
        prior_manifest_sha256=prior.manifest_sha256,
        current_manifest=current,
        changed_documents=changed_documents,
        preserved_review_ids=tuple(sorted(r.finding_id for r in preserved)),
        invalidated_review_ids=tuple(sorted(r.finding_id for r in invalidated)),
    )
