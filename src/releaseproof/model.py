from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()


class ReleaseState(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True, slots=True)
class Citation:
    document_id: str
    document_sha256: str
    page: int
    bounds: tuple[float, float, float, float]
    confidence: float
    label: str
    evidence_slice_sha256: str


@dataclass(frozen=True, slots=True)
class FieldValue:
    field: str
    value: str
    citation: Citation


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    document_id: str
    document_sha256: str
    dws_operation: str
    dws_receipt_sha256: str
    fields: tuple[FieldValue, ...]

    def by_field(self) -> dict[str, FieldValue]:
        return {item.field: item for item in self.fields}


@dataclass(frozen=True, slots=True)
class Finding:
    finding_id: str
    rule_id: str
    field: str
    severity: str
    state: ReleaseState
    message: str
    citations: tuple[Citation, ...]

    @property
    def binding(self) -> str:
        return digest({
            "finding_id": self.finding_id,
            "rule_id": self.rule_id,
            "field": self.field,
            "evidence_slices": [c.evidence_slice_sha256 for c in self.citations],
        })


@dataclass(frozen=True, slots=True)
class HumanReview:
    finding_id: str
    finding_binding: str
    decision: str
    reviewer: str
    rationale: str


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    manifest_version: str
    policy_version: str
    documents: tuple[ExtractedDocument, ...]
    findings: tuple[Finding, ...]
    reviews: tuple[HumanReview, ...]
    release_state: ReleaseState
    manifest_sha256: str = field(default="")

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "policy_version": self.policy_version,
            "documents": [asdict(x) for x in self.documents],
            "findings": [asdict(x) for x in self.findings],
            "reviews": [asdict(x) for x in self.reviews],
            "release_state": self.release_state.value,
        }


@dataclass(frozen=True, slots=True)
class ReverificationResult:
    prior_manifest_sha256: str
    current_manifest: ReleaseManifest
    changed_documents: tuple[str, ...]
    preserved_review_ids: tuple[str, ...]
    invalidated_review_ids: tuple[str, ...]
