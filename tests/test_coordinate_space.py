from dataclasses import replace

from releaseproof.dws import normalize_data_extraction
from releaseproof.model import EvidenceIdentity, evidence_identity_equivalent


CANONICAL_SPACE = "nutrient-processor-canonical-rendition/1"
LEGACY_SPACE = "nutrient-legacy-or-original-rendition/1"


def test_bbox_equivalence_requires_same_coordinate_space():
    assert "coordinate_space" in EvidenceIdentity.__dataclass_fields__
    canonical = EvidenceIdentity(
        "invoice",
        2,
        "shipment_id",
        "S-42",
        (100.0, 20.0, 160.0, 30.0),
        coordinate_space=CANONICAL_SPACE,
    )
    legacy = replace(canonical, coordinate_space=LEGACY_SPACE)
    assert not evidence_identity_equivalent(canonical, legacy, bbox_tolerance=2.0)


def test_native_data_extraction_marks_processor_canonical_coordinate_space():
    payload = {
        "status": 200,
        "output": {
            "data": {"shipment_id": "S-42"},
            "metadata": {
                "shipment_id": {
                    "bbox": {"x": 100, "y": 20, "width": 60, "height": 10},
                    "confidence": 0.95,
                    "match": "id_match",
                    "pageIndex": 0,
                    "pageNumber": 1,
                    "source_bboxes": [
                        {
                            "block_id": "b17",
                            "pageIndex": 0,
                            "pageNumber": 1,
                            "bbox": {"x": 100, "y": 20, "width": 60, "height": 10},
                        }
                    ],
                }
            },
            "pages": [{"page": 1, "width": 600, "height": 800}],
        },
    }
    doc = normalize_data_extraction(
        "invoice",
        b"%PDF-canonical\n%%EOF",
        payload,
        page_pdf_bytes={1: b"%PDF-canonical-page-1\n%%EOF"},
        schema_source="nutrient-studio",
    )
    citation = doc.by_field()["shipment_id"].citation
    assert getattr(citation, "coordinate_space", None) == CANONICAL_SPACE
    assert citation.identity().coordinate_space == CANONICAL_SPACE
