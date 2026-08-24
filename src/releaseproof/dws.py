from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Protocol

import requests

from .model import (
    Citation,
    ExtractedDocument,
    FieldValue,
    PageDigest,
    digest,
    normalize_evidence_value,
)


class DwsError(RuntimeError):
    pass


class Transport(Protocol):
    def build_json_content(self, path: Path) -> dict[str, Any]: ...


@dataclass
class NutrientDwsTransport:
    api_key: str
    endpoint: str = "https://api.nutrient.io/build"
    sign_endpoint: str = "https://api.nutrient.io/sign"
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "NutrientDwsTransport":
        key = os.environ.get("NUTRIENT_API_KEY")
        if not key:
            raise DwsError("NUTRIENT_API_KEY is required for live DWS execution")
        return cls(api_key=key)

    def _processor_pdf_request(
        self,
        pdf_bytes: bytes,
        *,
        filename: str,
        instructions: dict[str, Any],
    ) -> bytes:
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"document": (filename, pdf_bytes, "application/pdf")},
            data={"instructions": json.dumps(instructions)},
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise DwsError(f"DWS Processor returned HTTP {response.status_code}")
        if not response.content.startswith(b"%PDF-"):
            raise DwsError("DWS Processor response was not a PDF")
        return response.content

    def canonicalize_pdf(self, path: Path, *, ocr_language: str = "english") -> bytes:
        """Create the DWS-owned canonical rendition before extraction.

        OCR and flatten are Processor primitives. ReleaseProof deliberately does not
        implement local substitutes for either operation.
        """
        instructions = {
            "parts": [{"file": "document"}],
            "actions": [
                {"type": "ocr", "language": ocr_language},
                {"type": "flatten"},
            ],
        }
        return self._processor_pdf_request(
            path.read_bytes(),
            filename=path.name,
            instructions=instructions,
        )

    def isolate_page(self, canonical_pdf: bytes, *, page: int) -> bytes:
        """Use Processor page selection instead of a local PDF splitter."""
        if page < 1:
            raise ValueError("page must be one-based and positive")
        index = page - 1
        instructions = {
            "parts": [{"file": "document", "pages": {"start": index, "end": index}}]
        }
        return self._processor_pdf_request(
            canonical_pdf,
            filename="canonical.pdf",
            instructions=instructions,
        )

    def sign_pdf(self, pdf_bytes: bytes, *, filename: str = "release.pdf") -> bytes:
        response = requests.post(
            self.sign_endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": (filename, pdf_bytes, "application/pdf")},
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise DwsError(f"DWS signing returned HTTP {response.status_code}")
        if not response.content.startswith(b"%PDF-"):
            raise DwsError("DWS signing response was not a PDF")
        return response.content

    def build_json_content(self, path: Path) -> dict[str, Any]:
        """Historical Processor json-content path retained for accepted evidence."""
        instructions = {
            "parts": [{"file": "document"}],
            "output": {"type": "json-content", "keyValuePairs": True},
        }
        with path.open("rb") as fh:
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"document": (path.name, fh, "application/pdf")},
                data={"instructions": json.dumps(instructions)},
                timeout=self.timeout_seconds,
            )
        if response.status_code >= 400:
            raise DwsError(f"DWS returned HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise DwsError("DWS response was not JSON content") from exc


@dataclass
class NutrientDataExtractionTransport:
    api_key: str
    endpoint: str = "https://api.nutrient.io/extraction/extract"
    timeout_seconds: int = 300

    @classmethod
    def from_env(cls) -> "NutrientDataExtractionTransport":
        key = os.environ.get("NUTRIENT_DATA_EXTRACTION_API_KEY")
        if not key:
            raise DwsError(
                "NUTRIENT_DATA_EXTRACTION_API_KEY is required for live Data Extraction execution"
            )
        return cls(api_key=key)

    def extract_pdf(
        self,
        pdf_bytes: bytes,
        *,
        filename: str,
        schema: dict[str, Any],
        mode: str = "structure",
    ) -> dict[str, Any]:
        instructions = {
            "mode": mode,
            "schema": schema,
            "citationsEnabled": True,
        }
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": (filename, pdf_bytes, "application/pdf")},
            data={"instructions": json.dumps(instructions)},
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise DwsError(f"DWS Data Extraction returned HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise DwsError("DWS Data Extraction response was not JSON") from exc
        if not isinstance(payload, dict):
            raise DwsError("DWS Data Extraction response was not an object")
        return payload


def load_studio_schema_from_env() -> dict[str, Any]:
    """Load a schema exported/generated outside code, normally from Nutrient Studio."""
    raw = os.environ.get("NUTRIENT_EXTRACTION_SCHEMA_JSON")
    if not raw:
        raise DwsError(
            "NUTRIENT_EXTRACTION_SCHEMA_JSON is required; generate/refine the schema in Nutrient Studio"
        )
    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DwsError("NUTRIENT_EXTRACTION_SCHEMA_JSON is invalid JSON") from exc
    if not isinstance(schema, dict) or schema.get("type") != "object":
        raise DwsError("Nutrient extraction schema must be a JSON object schema")
    return schema


@dataclass
class FixtureTransport:
    payloads: dict[str, dict[str, Any]]

    def build_json_content(self, path: Path) -> dict[str, Any]:
        try:
            return self.payloads[path.name]
        except KeyError as exc:
            raise DwsError(f"no fixture for {path.name}") from exc


def _field_name(label: str) -> str:
    clean = []
    for ch in label.strip().lower():
        clean.append(ch if ch.isalnum() else "_")
    return "_".join(part for part in "".join(clean).split("_") if part)


def _confidence(value: Any) -> float:
    number = float(value)
    if number > 1.0:
        number /= 100.0
    if not 0.0 <= number <= 1.0:
        raise DwsError(f"DWS confidence out of range after normalization: {number}")
    return number


def _bbox_to_bounds(bbox: Any) -> tuple[float, float, float, float]:
    if not isinstance(bbox, dict):
        raise DwsError("DWS key-value bbox was not an object")
    required = ("left", "top", "width", "height")
    if not all(k in bbox for k in required):
        raise DwsError("DWS key-value bbox missing left/top/width/height")
    left, top, width, height = (float(bbox[k]) for k in required)
    if width < 0 or height < 0:
        raise DwsError("DWS key-value bbox width/height must be non-negative")
    return (left, top, left + width, top + height)


def _xywh_to_bounds(bbox: Any) -> tuple[float, float, float, float]:
    if not isinstance(bbox, dict):
        raise DwsError("DWS Data Extraction grounding bbox was not an object")
    required = ("x", "y", "width", "height")
    if not all(k in bbox for k in required):
        raise DwsError("DWS Data Extraction grounding missing bbox coordinates")
    x, y, width, height = (float(bbox[k]) for k in required)
    if width < 0 or height < 0:
        raise DwsError("DWS Data Extraction bbox width/height must be non-negative")
    return (x, y, x + width, y + height)


def _make_field(
    *,
    document_id: str,
    doc_sha: str,
    field: str,
    label: str,
    value: str,
    page: int,
    bounds: tuple[float, float, float, float],
    confidence: float,
    page_sha256: str = "",
    page_hash_source: str = "",
    source_evidence: tuple[str, ...] = (),
    reading_order: int | None = None,
) -> FieldValue:
    normalized_value = normalize_evidence_value(value)
    citation = Citation(
        document_id=document_id,
        document_sha256=doc_sha,
        page=page,
        bounds=bounds,
        confidence=confidence,
        label=label,
        evidence_slice_sha256=digest({
            "slice_schema": "releaseproof/evidence-slice/2",
            "document_id": document_id,
            "field_path": field,
            "normalized_value": normalized_value,
            "page": page,
            "bounds": list(bounds),
            "confidence": confidence,
            "source_evidence": list(source_evidence),
        }),
        field_path=field,
        normalized_value=normalized_value,
        page_sha256=page_sha256,
        page_hash_source=page_hash_source,
        source_evidence=source_evidence,
        reading_order=reading_order,
    )
    return FieldValue(field, value, citation)


def _fixture_page_digests(fields: list[FieldValue]) -> tuple[PageDigest, ...]:
    pages: dict[int, list[dict[str, Any]]] = {}
    for field in fields:
        pages.setdefault(field.citation.page, []).append({
            "field": field.field,
            "value": field.citation.normalized_value,
            "bounds": list(field.citation.bounds),
        })
    return tuple(
        PageDigest(page, digest(sorted(items, key=lambda item: item["field"])), "normalized-page-evidence")
        for page, items in sorted(pages.items())
    )


def normalize_fixture(document_id: str, document_bytes: bytes, payload: dict[str, Any]) -> ExtractedDocument:
    """Normalize deterministic test fixtures without claiming live DWS execution."""
    doc_sha = sha256(document_bytes).hexdigest()
    receipt_sha = digest(payload)
    fields: list[FieldValue] = []
    for item in payload.get("fields", []):
        confidence = _confidence(item["confidence"])
        bounds = tuple(float(x) for x in item["bounds"])
        if len(bounds) != 4:
            raise DwsError("fixture bounds must contain four numbers")
        fields.append(_make_field(
            document_id=document_id,
            doc_sha=doc_sha,
            field=str(item["field"]),
            label=str(item["label"]),
            value=str(item["value"]),
            page=int(item["page"]),
            bounds=bounds,
            confidence=confidence,
        ))
    explicit_page_digests = payload.get("page_digests")
    if explicit_page_digests is not None:
        if not isinstance(explicit_page_digests, list):
            raise DwsError("fixture page_digests must be an array")
        page_digests = tuple(
            PageDigest(int(item["page"]), str(item["sha256"]), "controlled-fixture-page")
            for item in explicit_page_digests
        )
    else:
        page_digests = _fixture_page_digests(fields)
    return ExtractedDocument(
        document_id,
        doc_sha,
        "controlled-fixture:nutrient-shaped",
        receipt_sha,
        tuple(fields),
        page_digests,
        "controlled-fixture",
    )


def normalize_processor_json(
    document_id: str,
    document_bytes: bytes,
    payload: dict[str, Any],
    *,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Normalize the historical hosted Processor json-content response."""
    aliases = {k.strip().lower(): v for k, v in (field_aliases or {}).items()}
    doc_sha = sha256(document_bytes).hexdigest()
    receipt_sha = digest(payload)
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise DwsError("DWS Processor JSON missing pages array")
    fields: list[FieldValue] = []
    page_digests: list[PageDigest] = []
    used_ordered_page_position = False
    for page_position, page_obj in enumerate(pages):
        if not isinstance(page_obj, dict):
            raise DwsError("DWS Processor page was not an object")
        if "pageIndex" in page_obj:
            page_index = page_obj["pageIndex"]
            if isinstance(page_index, bool) or not isinstance(page_index, int) or page_index < 0:
                raise DwsError("DWS Processor pageIndex present but invalid")
        else:
            page_index = page_position
            used_ordered_page_position = True
        page_number = page_index + 1
        page_sha = digest({"legacy_processor_page": page_obj})
        page_digests.append(PageDigest(page_number, page_sha, "processor-page-json-legacy"))
        pairs = page_obj.get("keyValuePairs", [])
        if not isinstance(pairs, list):
            raise DwsError("DWS Processor keyValuePairs was not an array")
        for pair in pairs:
            if not isinstance(pair, dict):
                raise DwsError("DWS Processor key-value pair was not an object")
            key = pair.get("key")
            value = pair.get("value")
            if not isinstance(key, dict) or not isinstance(value, dict):
                raise DwsError("DWS Processor key-value pair missing key/value objects")
            if "content" not in key or "content" not in value or "confidence" not in pair:
                raise DwsError("DWS Processor key-value pair missing grounding metadata")
            label = str(key["content"]).strip()
            raw_value = str(value["content"]).strip()
            if not label or not raw_value:
                raise DwsError("DWS Processor key-value pair had empty label/value")
            bounds = _bbox_to_bounds(value.get("bbox"))
            confidence = _confidence(pair["confidence"])
            field = aliases.get(label.lower(), _field_name(label))
            fields.append(_make_field(
                document_id=document_id,
                doc_sha=doc_sha,
                field=field,
                label=label,
                value=raw_value,
                page=page_number,
                bounds=bounds,
                confidence=confidence,
                page_sha256=page_sha,
                page_hash_source="processor-page-json-legacy",
            ))
    if not fields:
        raise DwsError("DWS Processor JSON contained no usable key-value pairs")
    source = "nutrient-dws:processor-json-content:keyValuePairs"
    if used_ordered_page_position:
        source += ":ordered-page-position"
    return ExtractedDocument(
        document_id,
        doc_sha,
        source,
        receipt_sha,
        tuple(fields),
        tuple(page_digests),
        "legacy-processor-kv",
    )


def normalize_spatial_json(
    document_id: str,
    document_bytes: bytes,
    payload: dict[str, Any],
    *,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Normalize the earlier controlled spatial-JSON adapter."""
    aliases = {k.strip().lower(): v for k, v in (field_aliases or {}).items()}
    doc_sha = sha256(document_bytes).hexdigest()
    receipt_sha = digest(payload)
    fields: list[FieldValue] = []
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise DwsError("DWS spatial JSON missing pages array")
    page_digests: list[PageDigest] = []
    for page_position, page_obj in enumerate(pages):
        if not isinstance(page_obj, dict):
            raise DwsError("DWS spatial JSON page was not an object")
        page_number = int(page_obj.get("page", page_position + 1))
        page_sha = digest({"spatial_page": page_obj})
        page_digests.append(PageDigest(page_number, page_sha, "data-extraction-spatial-page-json"))
        elements = page_obj.get("elements", [])
        if not isinstance(elements, list):
            raise DwsError("DWS spatial JSON elements was not an array")
        for item in elements:
            if not isinstance(item, dict) or item.get("type") != "key_value_pair":
                continue
            required = {"label", "value", "confidence", "page", "bounds"}
            if not required.issubset(item):
                raise DwsError("DWS key-value element missing grounding metadata")
            bounds = item["bounds"]
            if not isinstance(bounds, list) or len(bounds) != 4:
                raise DwsError("DWS key-value bounds must contain four numbers")
            label = str(item["label"])
            field = aliases.get(label.strip().lower(), _field_name(label))
            fields.append(_make_field(
                document_id=document_id,
                doc_sha=doc_sha,
                field=field,
                label=label,
                value=str(item["value"]),
                page=int(item["page"]),
                bounds=tuple(float(x) for x in bounds),
                confidence=_confidence(item["confidence"]),
                page_sha256=page_sha,
                page_hash_source="data-extraction-spatial-page-json",
            ))
    if not fields:
        raise DwsError("DWS spatial JSON contained no usable key-value elements")
    return ExtractedDocument(
        document_id,
        doc_sha,
        "nutrient-data-extraction:spatial-json",
        receipt_sha,
        tuple(fields),
        tuple(page_digests),
        "controlled-spatial-adapter",
    )


def _walk_extracted_values(
    data_node: Any,
    metadata_node: Any,
    *,
    path: str = "",
):
    if isinstance(data_node, dict):
        for key, value in data_node.items():
            child_meta = metadata_node.get(key, {}) if isinstance(metadata_node, dict) else {}
            child_path = f"{path}.{key}" if path else key
            yield from _walk_extracted_values(value, child_meta, path=child_path)
        return
    if isinstance(data_node, list):
        metadata_list = metadata_node if isinstance(metadata_node, list) else []
        for index, value in enumerate(data_node):
            child_meta = metadata_list[index] if index < len(metadata_list) else {}
            yield from _walk_extracted_values(value, child_meta, path=f"{path}[{index}]")
        return
    yield path, data_node, metadata_node


def normalize_data_extraction(
    document_id: str,
    canonical_document_bytes: bytes,
    payload: dict[str, Any],
    *,
    page_pdf_bytes: dict[int, bytes] | None = None,
    schema_source: str,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Normalize live-proven `/extraction/extract` data + metadata grounding."""
    aliases = field_aliases or {}
    output = payload.get("output")
    if not isinstance(output, dict):
        raise DwsError("DWS Data Extraction response missing output object")
    data = output.get("data")
    metadata = output.get("metadata")
    if not isinstance(data, (dict, list)) or not isinstance(metadata, (dict, list)):
        raise DwsError("DWS Data Extraction response missing data/metadata grounding")

    doc_sha = sha256(canonical_document_bytes).hexdigest()
    receipt_sha = digest(payload)
    actual_page_bytes = page_pdf_bytes or {}
    actual_page_digests = {
        page: PageDigest(page, sha256(page_bytes).hexdigest(), "canonical-page-pdf")
        for page, page_bytes in sorted(actual_page_bytes.items())
    }
    fields: list[FieldValue] = []
    pages_used: set[int] = set()

    for field_path, value, meta in _walk_extracted_values(data, metadata):
        if not field_path:
            continue
        if not isinstance(meta, dict):
            raise DwsError(f"DWS Data Extraction grounding missing for {field_path}")
        if "bbox" not in meta or "confidence" not in meta or "pageIndex" not in meta:
            raise DwsError(f"DWS Data Extraction grounding missing for {field_path}")
        page_index = meta["pageIndex"]
        if isinstance(page_index, bool) or not isinstance(page_index, int) or page_index < 0:
            raise DwsError(f"DWS Data Extraction pageIndex invalid for {field_path}")
        page = page_index + 1
        if "pageNumber" in meta and int(meta["pageNumber"]) != page:
            raise DwsError(f"DWS Data Extraction page reference conflict for {field_path}")
        bounds = _xywh_to_bounds(meta["bbox"])
        confidence = _confidence(meta["confidence"])
        source_bboxes = meta.get("source_bboxes", [])
        if not isinstance(source_bboxes, list):
            raise DwsError(f"DWS Data Extraction source evidence invalid for {field_path}")
        source_evidence = tuple(
            str(item["block_id"])
            for item in source_bboxes
            if isinstance(item, dict) and item.get("block_id") is not None
        )
        reading_order_raw = meta.get("readingOrder")
        reading_order = None if reading_order_raw is None else int(reading_order_raw)
        page_digest = actual_page_digests.get(page)
        page_sha = page_digest.sha256 if page_digest else ""
        page_hash_source = page_digest.source if page_digest else ""
        field = aliases.get(field_path, field_path)
        fields.append(_make_field(
            document_id=document_id,
            doc_sha=doc_sha,
            field=field,
            label=str(meta.get("match", field_path)),
            value=str(value),
            page=page,
            bounds=bounds,
            confidence=confidence,
            page_sha256=page_sha,
            page_hash_source=page_hash_source,
            source_evidence=source_evidence,
            reading_order=reading_order,
        ))
        pages_used.add(page)

    if not fields:
        raise DwsError("DWS Data Extraction response contained no grounded scalar fields")

    page_digests = tuple(
        actual_page_digests[page]
        for page in sorted(pages_used)
        if page in actual_page_digests
    )
    return ExtractedDocument(
        document_id,
        doc_sha,
        "nutrient-data-extraction:/extraction/extract",
        receipt_sha,
        tuple(fields),
        page_digests,
        schema_source,
    )


def process_with_native_dws(
    document_id: str,
    path: Path,
    processor: NutrientDwsTransport,
    extraction: NutrientDataExtractionTransport,
    *,
    schema: dict[str, Any],
    schema_source: str = "nutrient-studio",
    mode: str = "structure",
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Canonicalize with Processor, extract with Data Extraction, hash native page PDFs."""
    canonical_pdf = processor.canonicalize_pdf(path)
    payload = extraction.extract_pdf(
        canonical_pdf,
        filename=path.name,
        schema=schema,
        mode=mode,
    )
    output = payload.get("output", {})
    pages = output.get("pages", []) if isinstance(output, dict) else []
    page_numbers: list[int] = []
    if isinstance(pages, list):
        for index, page_info in enumerate(pages):
            if isinstance(page_info, dict) and "page" in page_info:
                page_numbers.append(int(page_info["page"]))
            else:
                page_numbers.append(index + 1)
    page_pdf_bytes = {
        page: processor.isolate_page(canonical_pdf, page=page)
        for page in sorted(set(page_numbers))
        if page >= 1
    }
    return normalize_data_extraction(
        document_id,
        canonical_pdf,
        payload,
        page_pdf_bytes=page_pdf_bytes,
        schema_source=schema_source,
        field_aliases=field_aliases,
    )


def process_with_dws(
    document_id: str,
    path: Path,
    transport: Transport,
    *,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Historical Processor acceptance path retained for reproducibility."""
    payload = transport.build_json_content(path)
    return normalize_processor_json(
        document_id,
        path.read_bytes(),
        payload,
        field_aliases=field_aliases,
    )
