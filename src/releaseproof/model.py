from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
import unicodedata
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()


def normalize_evidence_value(value: Any) -> str:
    """Normalize representation noise without inventing domain semantics."""
    text = unicodedata.normalize("NFKC", str(value))
    return " ".join(text.split())


class ReleaseState(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True, slots=True)
class EvidenceIdentity:
    document_id: str
    page: int
    field_path: str
    normalized_value: str
    bounds: tuple[float, float, float, float]

    def payload(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "page": self.page,
            "field_path": self.field_path,
            "normalized_value": self.normalized_value,
            "bounds": list(self.bounds),
        }


def evidence_identity_equivalent(
    left: EvidenceIdentity,
    right: EvidenceIdentity,
    *,
    bbox_tolerance: float = 2.0,
) -> bool:
    if bbox_tolerance < 0:
        raise ValueError("bbox_tolerance must be non-negative")
    if (
        left.document_id != right.document_id
        or left.page != right.page
        or left.field_path != right.field_path
        or left.normalized_value != right.normalized_value
    ):
        return False
    return all(abs(a - b) <= bbox_tolerance for a, b in zip(left.bounds, right.bounds, strict=True))


def evidence_sets_equivalent(
    left: tuple[EvidenceIdentity, ...],
    right: tuple[EvidenceIdentity, ...],
    *,
    bbox_tolerance: float = 2.0,
) -> bool:
    if len(left) != len(right):
        return False

    def key(item: EvidenceIdentity):
        return (item.document_id, item.page, item.field_path, item.normalized_value, item.bounds)

    unmatched = list(sorted(right, key=key))
    for item in sorted(left, key=key):
        match_index = next(
            (
                index
                for index, candidate in enumerate(unmatched)
                if evidence_identity_equivalent(item, candidate, bbox_tolerance=bbox_tolerance)
            ),
            None,
        )
        if match_index is None:
            return False
        unmatched.pop(match_index)
    return not unmatched


@dataclass(frozen=True, slots=True)
class PageDigest:
    page: int
    sha256: str
    source: str


@dataclass(frozen=True, slots=True)
class Citation:
    document_id: str
    document_sha256: str
    page: int
    bounds: tuple[float, float, float, float]
    confidence: float
    label: str
    evidence_slice_sha256: str
    field_path: str = ""
    normalized_value: str = ""
    page_sha256: str = ""
    page_hash_source: str = ""
    source_evidence: tuple[str, ...] = ()
    reading_order: int | None = None

    def identity(self, *, fallback_field_path: str = "") -> EvidenceIdentity:
        field_path = self.field_path or fallback_field_path
        if not field_path:
            raise ValueError("citation has no field path for semantic identity")
        return EvidenceIdentity(
            document_id=self.document_id,
            page=self.page,
            field_path=field_path,
            normalized_value=self.normalized_value,
            bounds=self.bounds,
        )


@dataclass(frozen=True, slots=True)
class FieldValue:
    field: str
    value: str
    citation: Citation

    @property
    def evidence_identity(self) -> EvidenceIdentity:
        normalized_value = self.citation.normalized_value or normalize_evidence_value(self.value)
        return EvidenceIdentity(
            document_id=self.citation.document_id,
            page=self.citation.page,
            field_path=self.citation.field_path or self.field,
            normalized_value=normalized_value,
            bounds=self.citation.bounds,
        )


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    document_id: str
    document_sha256: str
    dws_operation: str
    dws_receipt_sha256: str
    fields: tuple[FieldValue, ...]
    page_digests: tuple[PageDigest, ...] = ()
    schema_source: str = "legacy"

    def by_field(self) -> dict[str, FieldValue]:
        return {item.field: item for item in self.fields}

    def page_digest_map(self) -> dict[int, str]:
        return {item.page: item.sha256 for item in self.page_digests}


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
    def evidence_identities(self) -> tuple[EvidenceIdentity, ...]:
        return tuple(citation.identity(fallback_field_path=self.field) for citation in self.citations)

    @property
    def binding(self) -> str:
        return digest({
            "binding_schema": "releaseproof/semantic-finding-binding/2",
            "finding_id": self.finding_id,
            "rule_id": self.rule_id,
            "field": self.field,
            "evidence": [identity.payload() for identity in self.evidence_identities],
        })


@dataclass(frozen=True, slots=True)
class HumanReview:
    finding_id: str
    finding_binding: str
    decision: str
    reviewer: str
    rationale: str
    evidence_identities: tuple[EvidenceIdentity, ...] = ()


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
    changed_pages: tuple[tuple[str, int], ...] = ()
