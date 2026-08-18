"""Generate three small, non-sensitive, text PDFs for live Nutrient DWS acceptance.

The documents contain only synthetic trade data. They are intentionally generated at
runtime so no customer/private document needs to be stored in the public repository.
"""
from __future__ import annotations

from pathlib import Path


PACKET = {
    "invoice.pdf": [
        "COMMERCIAL INVOICE",
        "Shipment ID: SHP-260818-42",
        "Quantity: 100",
        "Currency: USD",
        "Declared Value: 25000",
    ],
    "shipping.pdf": [
        "BILL OF LADING",
        "Shipment ID: SHP-260818-42",
        "Quantity: 100",
        "Currency: USD",
        "Declared Value: 25000",
    ],
    "certificate.pdf": [
        "ORIGIN CERTIFICATE",
        "Shipment ID: SHP-260818-42",
        "Quantity: 100",
        "Currency: USD",
        "Declared Value: 25000",
    ],
}


def _pdf_bytes(lines: list[str]) -> bytes:
    # A minimal valid PDF 1.4 with one page and a Helvetica text content stream.
    commands = ["BT", "/F1 16 Tf", "72 730 Td"]
    for i, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if i:
            commands.append("0 -28 Td")
        commands.append(f"({escaped}) Tj")
    commands.append("ET")
    stream = ("\n".join(commands) + "\n").encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(
        (
            f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(out)


def main() -> int:
    target = Path("live-probe-input")
    target.mkdir(exist_ok=True)
    for filename, lines in PACKET.items():
        data = _pdf_bytes(lines)
        if not data.startswith(b"%PDF-") or not data.rstrip().endswith(b"%%EOF"):
            raise RuntimeError(f"invalid generated PDF envelope: {filename}")
        (target / filename).write_bytes(data)
        print(f"generated {target / filename} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
