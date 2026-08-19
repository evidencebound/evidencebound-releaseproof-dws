import pytest

from releaseproof.dws import DwsError, normalize_processor_json


def _pair(label: str, value: str, *, top: int = 20):
    return {
        "confidence": 97,
        "key": {
            "bbox": {"left": 10, "top": top, "width": 80, "height": 10},
            "content": label,
        },
        "value": {
            "bbox": {"left": 100, "top": top, "width": 60, "height": 10},
            "content": value,
            "dataType": "string",
        },
    }


def test_missing_page_index_uses_ordered_page_position_with_explicit_provenance():
    payload = {
        "pages": [
            {"plainText": "page one", "keyValuePairs": [_pair("Shipment ID", "S-42")]},
            {"plainText": "page two", "keyValuePairs": [_pair("Quantity", "100", top=40)]},
        ]
    }
    doc = normalize_processor_json(
        "invoice",
        b"%PDF-controlled",
        payload,
        field_aliases={"shipment id": "shipment_id"},
    )
    assert doc.by_field()["shipment_id"].citation.page == 1
    assert doc.by_field()["quantity"].citation.page == 2
    assert doc.dws_operation == (
        "nutrient-dws:processor-json-content:keyValuePairs:ordered-page-position"
    )


def test_documented_page_index_remains_authoritative():
    payload = {
        "pages": [
            {"pageIndex": 4, "keyValuePairs": [_pair("Shipment ID", "S-42")]},
        ]
    }
    doc = normalize_processor_json("shipping", b"pdf", payload)
    field = doc.by_field()["shipment_id"]
    assert field.citation.page == 5
    assert doc.dws_operation == "nutrient-dws:processor-json-content:keyValuePairs"


@pytest.mark.parametrize("invalid", ["0", None, True, -1])
def test_present_invalid_page_index_still_fails_closed(invalid):
    payload = {
        "pages": [
            {"pageIndex": invalid, "keyValuePairs": [_pair("Quantity", "100")]},
        ]
    }
    with pytest.raises(DwsError, match="pageIndex present but invalid"):
        normalize_processor_json("invoice", b"pdf", payload)


def test_missing_page_index_does_not_relax_other_grounding_requirements():
    payload = {
        "pages": [
            {
                "plainText": "page one",
                "keyValuePairs": [
                    {
                        "confidence": 97,
                        "key": {"content": "Quantity"},
                        "value": {"content": "100"},
                    }
                ],
            }
        ]
    }
    with pytest.raises(DwsError, match="bbox"):
        normalize_processor_json("invoice", b"pdf", payload)
