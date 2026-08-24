import json

import pytest

from releaseproof.dws import (
    DwsError,
    NutrientDataExtractionTransport,
    NutrientDwsTransport,
    normalize_data_extraction,
)
from releaseproof.viewer import project_finding_for_viewer
from releaseproof.engine import build_manifest
from releaseproof.demo import load_demo_documents


def test_processor_canonicalization_uses_native_ocr_and_flatten(monkeypatch, tmp_path):
    captured = {}

    class Response:
        status_code = 200
        content = b"%PDF-canonical\n%%EOF"

    def fake_post(endpoint, headers, files, data, timeout):
        captured["endpoint"] = endpoint
        captured["headers"] = headers
        captured["instructions"] = json.loads(data["instructions"])
        return Response()

    monkeypatch.setattr("releaseproof.dws.requests.post", fake_post)
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF-source\n%%EOF")
    result = NutrientDwsTransport("test-key").canonicalize_pdf(path)
    assert result.startswith(b"%PDF-canonical")
    assert captured["endpoint"] == "https://api.nutrient.io/build"
    assert captured["instructions"] == {
        "parts": [{"file": "document"}],
        "actions": [
            {"type": "ocr", "language": "english"},
            {"type": "flatten"},
        ],
    }


def test_processor_page_isolation_uses_native_pages_selection(monkeypatch):
    captured = {}

    class Response:
        status_code = 200
        content = b"%PDF-page-7\n%%EOF"

    def fake_post(endpoint, headers, files, data, timeout):
        captured["instructions"] = json.loads(data["instructions"])
        return Response()

    monkeypatch.setattr("releaseproof.dws.requests.post", fake_post)
    result = NutrientDwsTransport("test-key").isolate_page(b"%PDF-canonical\n%%EOF", page=7)
    assert result.startswith(b"%PDF-page-7")
    assert captured["instructions"] == {
        "parts": [{"file": "document", "pages": {"start": 6, "end": 6}}]
    }


def test_data_extraction_request_matches_live_proven_nutrient_sample(monkeypatch):
    captured = {}

    class Response:
        status_code = 200
        def json(self):
            return {"status": 200, "output": {"data": {}, "metadata": {}, "pages": []}}

    def fake_post(endpoint, headers, files, data, timeout):
        captured["endpoint"] = endpoint
        captured["headers"] = headers
        captured["filename"] = files["file"][0]
        captured["instructions"] = json.loads(data["instructions"])
        return Response()

    monkeypatch.setattr("releaseproof.dws.requests.post", fake_post)
    schema = {"type": "object", "properties": {"shipment_id": {"type": "string"}}}
    payload = NutrientDataExtractionTransport("extract-key").extract_pdf(
        b"%PDF-canonical\n%%EOF",
        filename="invoice.pdf",
        schema=schema,
        mode="structure",
    )
    assert payload["status"] == 200
    assert captured["endpoint"] == "https://api.nutrient.io/extraction/extract"
    assert captured["instructions"] == {
        "mode": "structure",
        "schema": schema,
        "citationsEnabled": True,
    }


def test_data_extraction_normalizer_uses_provider_metadata_not_custom_grounding():
    payload = {
        "status": 200,
        "output": {
            "data": {"shipment_id": "S-42", "quantity": 100},
            "metadata": {
                "shipment_id": {
                    "bbox": {"x": 100, "y": 20, "width": 60, "height": 10},
                    "confidence": 0.95,
                    "match": "id_match",
                    "pageIndex": 1,
                    "pageNumber": 2,
                    "source_bboxes": [{"block_id": "b17", "pageIndex": 1, "pageNumber": 2, "bbox": {"x": 100, "y": 20, "width": 60, "height": 10}}],
                },
                "quantity": {
                    "bbox": {"x": 200, "y": 20, "width": 40, "height": 10},
                    "confidence": 0.97,
                    "match": "id_match",
                    "pageIndex": 1,
                    "pageNumber": 2,
                    "source_bboxes": [{"block_id": "b18", "pageIndex": 1, "pageNumber": 2, "bbox": {"x": 200, "y": 20, "width": 40, "height": 10}}],
                },
            },
            "pages": [{"page": 1, "width": 600, "height": 800}, {"page": 2, "width": 600, "height": 800}],
        },
    }
    doc = normalize_data_extraction(
        "invoice",
        b"%PDF-canonical\n%%EOF",
        payload,
        page_pdf_bytes={2: b"%PDF-canonical-page-2\n%%EOF"},
        schema_source="nutrient-studio",
    )
    shipment = doc.by_field()["shipment_id"]
    assert shipment.citation.page == 2
    assert shipment.citation.bounds == (100.0, 20.0, 160.0, 30.0)
    assert shipment.citation.confidence == pytest.approx(0.95)
    assert shipment.citation.source_evidence == ("b17",)
    assert shipment.citation.field_path == "shipment_id"
    assert shipment.citation.normalized_value == "S-42"
    assert doc.schema_source == "nutrient-studio"
    assert doc.page_digests[0].page == 2
    assert doc.page_digests[0].source == "canonical-page-pdf"


def test_data_extraction_missing_bbox_fails_closed():
    payload = {
        "status": 200,
        "output": {
            "data": {"shipment_id": "S-42"},
            "metadata": {"shipment_id": {"confidence": 0.95, "pageIndex": 0}},
            "pages": [{"page": 1, "width": 600, "height": 800}],
        },
    }
    with pytest.raises(DwsError, match="grounding"):
        normalize_data_extraction("invoice", b"pdf", payload, schema_source="nutrient-studio")


def test_viewer_projection_uses_annotation_reviewer_layer_comment_and_approved_layer():
    manifest = build_manifest(load_demo_documents())
    finding = next(f for f in manifest.findings if f.state.value == "REVIEW_REQUIRED")
    projection = project_finding_for_viewer(finding, reviewer="reviewer-1")
    assert projection.annotation.page_index == finding.citations[0].page - 1
    assert projection.annotation.bounds == finding.citations[0].bounds
    assert projection.reviewer_layer == "releaseproof/reviewer/reviewer-1"
    assert projection.approved_layer == "releaseproof/approved"
    assert projection.comment.finding_id == finding.finding_id


def test_signing_adapter_uses_processor_sign_endpoint(monkeypatch):
    captured = {}

    class Response:
        status_code = 200
        content = b"%PDF-signed\n%%EOF"

    def fake_post(endpoint, headers, files, timeout):
        captured["endpoint"] = endpoint
        captured["headers"] = headers
        captured["filename"] = files["file"][0]
        return Response()

    monkeypatch.setattr("releaseproof.dws.requests.post", fake_post)
    signed = NutrientDwsTransport("test-key").sign_pdf(b"%PDF-release\n%%EOF", filename="release.pdf")
    assert signed.startswith(b"%PDF-signed")
    assert captured["endpoint"] == "https://api.nutrient.io/sign"
    assert captured["filename"] == "release.pdf"
