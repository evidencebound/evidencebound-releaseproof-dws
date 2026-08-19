from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Protocol

import requests

from .model import Citation, ExtractedDocument, FieldValue, digest


class DwsError(RuntimeError):
    pass


class Transport(Protocol):
    def build_json_content(self, path: Path) -> dict[str, Any]: ...


@dataclass
class NutrientDwsTransport:
    api_key: str
    endpoint: str = "https://api.nutrient.io/build"
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "NutrientDwsTransport":
        key = os.environ.get("NUTRIENT_API_KEY")
        if not key:
            raise DwsError("NUTRIENT_API_KEY is required for live DWS execution")
        return cls(api_key=key)

    def build_json_content(self, path: Path) -> dict[str, Any]:
        # Exact hosted Processor pattern from Nutrient's public DWS example:
        # /build -> json-content -> keyValuePairs. We intentionally keep the
        # request minimal rather than inventing undocumented extraction actions.
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
    number=float(value)
    # Processor examples expose percentage-like confidence (e.g. 95.4), while
    # spatial JSON examples expose 0..1. Normalize both into 0..1 and reject
    # impossible values rather than silently clipping them.
    if number > 1.0:
        number /= 100.0
    if not 0.0 <= number <= 1.0:
        raise DwsError(f"DWS confidence out of range after normalization: {number}")
    return number


def _bbox_to_bounds(bbox: Any) -> tuple[float, float, float, float]:
    if not isinstance(bbox, dict):
        raise DwsError("DWS key-value bbox was not an object")
    required=("left","top","width","height")
    if not all(k in bbox for k in required):
        raise DwsError("DWS key-value bbox missing left/top/width/height")
    left,top,width,height=(float(bbox[k]) for k in required)
    if width < 0 or height < 0:
        raise DwsError("DWS key-value bbox width/height must be non-negative")
    return (left,top,left+width,top+height)


def _make_field(
    *, document_id: str, doc_sha: str, field: str, label: str, value: str,
    page: int, bounds: tuple[float,float,float,float], confidence: float,
) -> FieldValue:
    citation = Citation(
        document_id=document_id,
        document_sha256=doc_sha,
        page=page,
        bounds=bounds,
        confidence=confidence,
        label=label,
        evidence_slice_sha256=digest({
            "slice_schema":"releaseproof/evidence-slice/1",
            "document_id":document_id,
            "field":field,
            "label":label,"value":value,"page":page,
            "bounds":list(bounds),"confidence":confidence,
        }),
    )
    return FieldValue(field,value,citation)


def normalize_fixture(document_id: str, document_bytes: bytes, payload: dict[str, Any]) -> ExtractedDocument:
    """Normalize deterministic test fixtures without claiming live DWS execution."""
    doc_sha = sha256(document_bytes).hexdigest()
    receipt_sha = digest(payload)
    fields = []
    for item in payload.get("fields", []):
        confidence=_confidence(item["confidence"])
        bounds=tuple(float(x) for x in item["bounds"])
        if len(bounds)!=4:
            raise DwsError("fixture bounds must contain four numbers")
        fields.append(_make_field(
            document_id=document_id, doc_sha=doc_sha, field=str(item["field"]),
            label=str(item["label"]), value=str(item["value"]), page=int(item["page"]),
            bounds=bounds, confidence=confidence,
        ))
    return ExtractedDocument(
        document_id, doc_sha, "controlled-fixture:nutrient-shaped", receipt_sha, tuple(fields)
    )


def normalize_processor_json(
    document_id: str,
    document_bytes: bytes,
    payload: dict[str, Any],
    *,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Normalize DWS Processor ``json-content`` key-value output.

    Nutrient's documented examples expose ``pages[].pageIndex``. A live acceptance
    run on 2026-08-19 observed a compatible ordered ``pages[]`` array whose page
    objects contained ``plainText`` and ``keyValuePairs`` but omitted ``pageIndex``.

    When ``pageIndex`` is present, it remains authoritative and must be a
    non-negative integer. When it is absent, ReleaseProof uses the deterministic
    zero-based position of that page object in the returned ``pages[]`` array and
    marks the extraction source with ``ordered-page-position``. A present but
    malformed index still fails closed; this compatibility path never guesses an
    arbitrary page number.
    """
    aliases={k.strip().lower():v for k,v in (field_aliases or {}).items()}
    doc_sha=sha256(document_bytes).hexdigest()
    receipt_sha=digest(payload)
    pages=payload.get("pages")
    if not isinstance(pages,list):
        raise DwsError("DWS Processor JSON missing pages array")
    fields:list[FieldValue]=[]
    used_ordered_page_position=False
    for page_position, page_obj in enumerate(pages):
        if not isinstance(page_obj,dict):
            raise DwsError("DWS Processor page was not an object")
        if "pageIndex" in page_obj:
            page_index=page_obj["pageIndex"]
            if isinstance(page_index,bool) or not isinstance(page_index,int) or page_index < 0:
                raise DwsError("DWS Processor pageIndex present but invalid")
        else:
            page_index=page_position
            used_ordered_page_position=True
        pairs=page_obj.get("keyValuePairs",[])
        if not isinstance(pairs,list):
            raise DwsError("DWS Processor keyValuePairs was not an array")
        for pair in pairs:
            if not isinstance(pair,dict):
                raise DwsError("DWS Processor key-value pair was not an object")
            key=pair.get("key"); value=pair.get("value")
            if not isinstance(key,dict) or not isinstance(value,dict):
                raise DwsError("DWS Processor key-value pair missing key/value objects")
            if "content" not in key or "content" not in value or "confidence" not in pair:
                raise DwsError("DWS Processor key-value pair missing grounding metadata")
            label=str(key["content"]).strip(); raw_value=str(value["content"]).strip()
            if not label or not raw_value:
                raise DwsError("DWS Processor key-value pair had empty label/value")
            bounds=_bbox_to_bounds(value.get("bbox"))
            confidence=_confidence(pair["confidence"])
            field=aliases.get(label.lower(),_field_name(label))
            fields.append(_make_field(
                document_id=document_id,doc_sha=doc_sha,field=field,label=label,value=raw_value,
                page=page_index+1,bounds=bounds,confidence=confidence,
            ))
    if not fields:
        raise DwsError("DWS Processor JSON contained no usable key-value pairs")
    source="nutrient-dws:processor-json-content:keyValuePairs"
    if used_ordered_page_position:
        source += ":ordered-page-position"
    return ExtractedDocument(document_id,doc_sha,source,receipt_sha,tuple(fields))


def normalize_spatial_json(
    document_id: str,
    document_bytes: bytes,
    payload: dict[str, Any],
    *,
    field_aliases: dict[str, str] | None = None,
) -> ExtractedDocument:
    """Normalize Nutrient Data Extraction spatial JSON examples.

    Kept as an optional adapter because current public Nutrient materials describe
    spatial JSON separately from Processor ``/build``. The competition's live path
    uses ``normalize_processor_json`` unless a separately verified Data Extraction
    endpoint is adopted.
    """
    aliases = {k.strip().lower(): v for k, v in (field_aliases or {}).items()}
    doc_sha = sha256(document_bytes).hexdigest()
    receipt_sha = digest(payload)
    fields: list[FieldValue] = []
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise DwsError("DWS spatial JSON missing pages array")
    for page_obj in pages:
        if not isinstance(page_obj, dict):
            raise DwsError("DWS spatial JSON page was not an object")
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
                document_id=document_id,doc_sha=doc_sha,field=field,label=label,
                value=str(item["value"]),page=int(item["page"]),
                bounds=tuple(float(x) for x in bounds),confidence=_confidence(item["confidence"]),
            ))
    if not fields:
        raise DwsError("DWS spatial JSON contained no usable key-value elements")
    return ExtractedDocument(document_id, doc_sha, "nutrient-data-extraction:spatial-json", receipt_sha, tuple(fields))


def process_with_dws(
    document_id: str,
    path: Path,
    transport: Transport,
    *,
    field_aliases: dict[str,str] | None=None,
) -> ExtractedDocument:
    payload=transport.build_json_content(path)
    return normalize_processor_json(document_id,path.read_bytes(),payload,field_aliases=field_aliases)
