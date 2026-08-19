"""Create a byte-different but render-equivalent invoice for live reverification.

The revision inserts a PDF comment immediately before %%EOF. Object offsets, page
content, field locations, and rendered text are unchanged; only the file bytes and
therefore the document SHA-256 change. This is a controlled non-material revision.
"""
from __future__ import annotations

from pathlib import Path

from generate_synthetic_trade_pdfs import main as generate_packet


def main() -> int:
    generate_packet()
    source = Path("live-probe-input/invoice.pdf")
    target_dir = Path("live-probe-revision")
    target_dir.mkdir(exist_ok=True)
    target = target_dir / "invoice-revised.pdf"
    data = source.read_bytes()
    marker = b"%%EOF\n"
    if not data.endswith(marker):
        raise RuntimeError("base invoice PDF does not end with expected EOF marker")
    revised = data[:-len(marker)] + b"% ReleaseProof nonmaterial revision B\n" + marker
    if revised == data:
        raise RuntimeError("revision did not change bytes")
    if not revised.startswith(b"%PDF-") or not revised.rstrip().endswith(b"%%EOF"):
        raise RuntimeError("revised PDF envelope invalid")
    target.write_bytes(revised)
    print(f"generated {target} ({len(revised)} bytes); rendered page content unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
