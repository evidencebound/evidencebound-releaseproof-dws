from __future__ import annotations
from dataclasses import asdict, dataclass

from .demo import load_demo_documents
from .engine import build_manifest, differential_reverify, review_finding
from .model import ReleaseState


@dataclass(frozen=True, slots=True)
class Evaluation:
    prior_human_reviews: int
    blanket_review_reuse_after_nonmaterial_file_change: int
    differential_review_reuse_after_nonmaterial_file_change: int
    differential_review_reuse_fraction_after_nonmaterial_file_change: float
    invalidated_reviews_after_reviewed_slice_change: int
    preserved_reviews_after_reviewed_slice_change: int
    nonmaterial_current_state: str
    reviewed_slice_change_current_state: str
    changed_document_count_nonmaterial: int


def run_evaluation() -> Evaluation:
    base=build_manifest(load_demo_documents())
    reviewed=base
    for finding in base.findings:
        if finding.state == ReleaseState.REVIEW_REQUIRED:
            reviewed=review_finding(
                reviewed, finding.finding_id, 'evaluation-reviewer',
                'APPROVE_EXCEPTION', 'reviewed exact source-grounded slice',
            )
    prior_reviews=len(reviewed.reviews)
    nonmaterial=differential_reverify(reviewed,load_demo_documents(nonmaterial_invoice=True))
    material=differential_reverify(reviewed,load_demo_documents(reviewed_invoice_changed=True))
    return Evaluation(
        prior_human_reviews=prior_reviews,
        # Whole-file invalidation baseline discards all prior reviews after any changed hash.
        blanket_review_reuse_after_nonmaterial_file_change=0 if nonmaterial.changed_documents else prior_reviews,
        differential_review_reuse_after_nonmaterial_file_change=len(nonmaterial.preserved_review_ids),
        differential_review_reuse_fraction_after_nonmaterial_file_change=(
            len(nonmaterial.preserved_review_ids)/prior_reviews if prior_reviews else 1.0
        ),
        invalidated_reviews_after_reviewed_slice_change=len(material.invalidated_review_ids),
        preserved_reviews_after_reviewed_slice_change=len(material.preserved_review_ids),
        nonmaterial_current_state=nonmaterial.current_manifest.release_state.value,
        reviewed_slice_change_current_state=material.current_manifest.release_state.value,
        changed_document_count_nonmaterial=len(nonmaterial.changed_documents),
    )
