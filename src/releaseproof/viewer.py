from __future__ import annotations

from dataclasses import dataclass

from .model import Finding


@dataclass(frozen=True, slots=True)
class ViewerAnnotation:
    finding_id: str
    page_index: int
    bounds: tuple[float, float, float, float]
    annotation_kind: str = "rectangle"


@dataclass(frozen=True, slots=True)
class ViewerReviewComment:
    finding_id: str
    text: str


@dataclass(frozen=True, slots=True)
class ViewerReviewProjection:
    """Provider-neutral projection onto DWS Viewer-native review primitives.

    This object is not a second review database and is not presented as a hosted
    Viewer API wire payload. It describes how a ReleaseProof finding maps to the
    Viewer capabilities Nutrient recommended: a source annotation, a reviewer-
    specific layer/comment, and a named approved-state layer.
    """

    annotation: ViewerAnnotation
    reviewer_layer: str
    approved_layer: str
    comment: ViewerReviewComment


def _safe_layer_component(value: str) -> str:
    cleaned = value.strip().replace("/", "_")
    if not cleaned:
        raise ValueError("reviewer must be non-empty")
    return cleaned


def project_finding_for_viewer(
    finding: Finding,
    *,
    reviewer: str,
) -> ViewerReviewProjection:
    if not finding.citations:
        raise ValueError("finding has no grounded citation for Viewer projection")
    citation = finding.citations[0]
    reviewer_id = _safe_layer_component(reviewer)
    return ViewerReviewProjection(
        annotation=ViewerAnnotation(
            finding_id=finding.finding_id,
            page_index=citation.page - 1,
            bounds=citation.bounds,
        ),
        reviewer_layer=f"releaseproof/reviewer/{reviewer_id}",
        approved_layer="releaseproof/approved",
        comment=ViewerReviewComment(
            finding_id=finding.finding_id,
            text=f"ReleaseProof review for {finding.rule_id}:{finding.field}",
        ),
    )
