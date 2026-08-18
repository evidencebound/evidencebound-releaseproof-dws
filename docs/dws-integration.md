# Nutrient DWS Integration Contract

## Core hosted operation

ReleaseProof uses Nutrient DWS for a core document operation rather than a cosmetic call. The implemented live transport sends each PDF to:

```text
POST https://api.nutrient.io/build
```

with Processor instructions equivalent to:

```json
{
  "parts": [{"file": "document"}],
  "output": {"type": "json-content", "keyValuePairs": true}
}
```

The code intentionally does **not** invent an undocumented OCR action. The live response is normalized from the documented Processor `json-content` key-value shape.

## Processor response grounding required by ReleaseProof

`normalize_processor_json()` requires:

- `pages[].pageIndex`;
- `pages[].keyValuePairs[]`;
- pair `confidence`;
- `key.content` and `value.content`;
- `value.bbox` with `left`, `top`, `width`, `height`.

The normalizer converts the bbox to a four-coordinate evidence location, binds the source-file SHA-256 and complete DWS response digest, and refuses empty/malformed grounding. Confidence may be represented as `0..1` or percentage-like `0..100` and is normalized to `0..1`; out-of-range values fail closed.

`normalize_spatial_json()` remains a separate optional adapter for Nutrient Data Extraction spatial-JSON examples. It is not silently substituted for the Processor live path.

## Live acceptance script

```bash
NUTRIENT_API_KEY=... PYTHONPATH=src python scripts/run_live_dws_probe.py \
  --invoice path/to/invoice.pdf \
  --shipping path/to/shipping.pdf \
  --certificate path/to/certificate.pdf
```

The script has **no fixture fallback**. Live acceptance requires all three documents to be processed by DWS and the resulting current manifest/findings emitted with `execution: LIVE_NUTRIENT_DWS`.

## Current boundary

Live Nutrient execution is **UNVERIFIED/BLOCKED by network** in the current runtime. A user-controlled API key was supplied transiently for an acceptance attempt on 2026-08-18, but the sandbox could not resolve `api.nutrient.io`, so no HTTP response was obtained. The key is not persisted. The controlled demo proves the ReleaseProof mechanism only.
