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

The code intentionally does **not** invent an undocumented OCR action. The live response is normalized from Processor `json-content` key-value output.

## Processor response grounding required by ReleaseProof

`normalize_processor_json()` requires:

- ordered `pages[]`;
- `pages[].keyValuePairs[]`;
- pair `confidence`;
- `key.content` and `value.content`;
- `value.bbox` with `left`, `top`, `width`, `height`.

### Page identity compatibility rule

Nutrient's documented Processor examples expose `pages[].pageIndex`. A real hosted `/build` acceptance run on **2026-08-19** returned a one-page `pages[]` object containing `plainText` and `keyValuePairs`, but **no `pageIndex`**. The same live shape retained key/value bbox grounding and integer confidence.

ReleaseProof therefore applies this narrow compatibility rule:

1. if `pageIndex` is present, it is authoritative and must be a non-negative integer;
2. if `pageIndex` is absent, the zero-based position of the page object in the returned ordered `pages[]` array is used deterministically;
3. any extraction using this compatibility path is explicitly marked `nutrient-dws:processor-json-content:keyValuePairs:ordered-page-position`;
4. a present but malformed/negative `pageIndex` still fails closed;
5. no bbox, confidence, label or value requirement is relaxed.

This is a compatibility response to observed provider behavior, not a claim that the provider contract formally guarantees omission-safe page ordering in every future version. A changed response shape must pass the same live acceptance gate again.

The normalizer converts the bbox to a four-coordinate evidence location, binds the source-file SHA-256 and complete DWS response digest, and refuses empty/malformed grounding. Confidence may be represented as `0..1` or percentage-like `0..100` and is normalized to `0..1`; out-of-range values fail closed.

`normalize_spatial_json()` remains a separate optional adapter for Nutrient Data Extraction spatial-JSON examples. It is not silently substituted for the Processor live path.

## Live acceptance automation

The repository includes `.github/workflows/live-dws.yml`. It:

- reads `NUTRIENT_API_KEY` only from GitHub Actions secrets;
- generates three non-sensitive synthetic trade PDFs at runtime;
- invokes the hosted DWS `/build` path with no fixture fallback;
- verifies page, bbox, confidence and evidence-slice grounding;
- requires all three documents and a release manifest before the `LIVE_NUTRIENT_DWS` truth marker can pass;
- contains a quota-aware hosted Differential Reverification phase that reuses accepted base evidence and sends only the revised invoice as the fourth hosted call;
- publishes a sanitized run receipt to issue #3;
- never publishes the API key, Authorization header, or extracted document text.

A schema-only diagnostic is available for provider drift. It emits object keys, list lengths and scalar types only.

## Accepted live evidence

Observed on 2026-08-19:

- repository secret gate: **PASS**;
- GitHub-runner network path to hosted DWS: **PASS**;
- hosted `/build` returned parseable JSON: **PASS**;
- first strict live normalization: **FAIL** because the live page omitted documented `pageIndex`;
- schema-only diagnostic: **PASS** and confirmed `pages[] -> {plainText, keyValuePairs}` with grounded key/value objects;
- compatibility regression CI: **PASS** on Python 3.11 / 3.12 / 3.13;
- post-fix three-document hosted acceptance: **PASS**;
- field-level source-grounding assertions: **PASS**;
- current manifest generation: **PASS**;
- live release state: `REVIEW_REQUIRED` after a real cross-document extraction disagreement.

Canonical core run: `32215337912`. Artifact `9352133498` has digest `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`.

## Differential Reverification live boundary

The controlled mechanism already verifies both selective preservation and invalidation behavior. A hosted non-material-revision harness was added to test whether the same evidence binding remains stable across repeated real DWS extraction.

The first live harness redundantly reprocessed the base packet and reached HTTP `402` before the revised-document result could be produced. It was optimized to four total hosted calls, and that quota-aware harness passed public CI. On the next hosted run (`32215515505`), the provider/account returned HTTP `402` on the **first** `/build`; the schema diagnostic request also returned `402`.

No additional live DWS calls were made after that point. Correct status:

- `live_nutrient_dws_core`: **PASS**;
- deterministic Differential Reverification: **PASS**;
- hosted Differential Reverification: **BLOCKED_QUOTA_402**.

See `docs/live-dws-evidence.md` for the evidence ledger.
