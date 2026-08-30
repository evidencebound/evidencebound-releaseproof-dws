from releaseproof.dws import process_with_native_dws


class FakeProcessor:
    def __init__(self):
        self.isolated_pages = []

    def canonicalize_pdf(self, path):
        return b"%PDF-canonical\n%%EOF"

    def isolate_page(self, canonical_pdf, *, page):
        self.isolated_pages.append(page)
        return f"%PDF-canonical-page-{page}\n%%EOF".encode()


class FakeExtraction:
    def extract_pdf(self, pdf_bytes, *, filename, schema, mode):
        return {
            "status": 200,
            "output": {
                "data": {"shipment_id": "S-42"},
                "metadata": {
                    "shipment_id": {
                        "bbox": {"x": 100, "y": 20, "width": 60, "height": 10},
                        "confidence": 0.95,
                        "match": "id_match",
                        "pageIndex": 1,
                        "pageNumber": 2,
                        "source_bboxes": [
                            {
                                "block_id": "b17",
                                "pageIndex": 1,
                                "pageNumber": 2,
                                "bbox": {"x": 100, "y": 20, "width": 60, "height": 10},
                            }
                        ],
                    }
                },
            },
        }


def test_native_pipeline_hashes_pages_used_by_grounded_fields_even_without_output_pages(tmp_path):
    source = tmp_path / "invoice.pdf"
    source.write_bytes(b"%PDF-source\n%%EOF")
    processor = FakeProcessor()

    doc = process_with_native_dws(
        "invoice",
        source,
        processor,
        FakeExtraction(),
        schema={"type": "object", "properties": {"shipment_id": {"type": "string"}}},
        schema_source="acceptance-test-schema",
    )

    assert processor.isolated_pages == [2]
    assert len(doc.page_digests) == 1
    assert doc.page_digests[0].page == 2
    assert doc.page_digests[0].source == "canonical-page-pdf"
    shipment = doc.by_field()["shipment_id"]
    assert shipment.citation.page_sha256 == doc.page_digests[0].sha256
    assert shipment.citation.page_hash_source == "canonical-page-pdf"
    assert shipment.citation.coordinate_space == "nutrient-processor-canonical-rendition/1"
