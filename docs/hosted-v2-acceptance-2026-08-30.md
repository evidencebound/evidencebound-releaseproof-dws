# Hosted DWS v2 Acceptance - 2026-08-30

## Decision

**Overall DWS-native v2 acceptance: FAIL_PARTIAL_HOSTED.**

This is no longer an `UNRUN` state. One bounded hosted attempt was executed after hackathon event credits were confirmed added to the Nutrient organization account.

## Immutable run evidence

- GitHub Actions workflow: `live-dws-v2`
- run id: `33295050008`
- trigger commit: `987c3a7a7a13605d7cd9c5e7a1433648d42cfd81`
- hosted job id: `99213156711`
- artifact id: `9727139742`
- artifact name: `live-dws-v2-acceptance`
- artifact ZIP SHA-256: `6f9cb20f5439b12a5ee674ca859521f0fac1778563f99c532e2f4d7a466d7986`
- artifact size: 430 bytes

The artifact contains only the sanitized JSON receipt. No API key, Authorization header, raw provider payload, or private document content is retained.

## Provider-call ledger

Observed calls before fail-closed termination:

```json
{
  "processor": {
    "canonicalize": 1,
    "isolate_page": 0,
    "sign": 0
  },
  "data_extraction": 1
}
```

Observed result:

- Processor OCR + flatten canonicalization: **PASS_HOSTED**
- Data Extraction `/extraction/extract`: **FAIL_HTTP_403**
- canonical page isolation: **UNRUN_AFTER_UPSTREAM_FAILURE**
- differential reverification on hosted v2 evidence: **UNRUN_AFTER_UPSTREAM_FAILURE**
- Processor signing: **UNRUN_AFTER_UPSTREAM_FAILURE**
- Viewer hosted review flow: **UNRUN**

## Root cause

The run used the historical Processor credential for both Processor and Data Extraction. Processor accepted that credential and canonicalization completed. Data Extraction rejected the first request with HTTP 403.

Current official Nutrient sample material states that Data Extraction uses a product key separate from the Processor API key. The request wire shape itself matches Nutrient's live-proven sample (`file` plus JSON `instructions` containing `mode`, `schema`, and `citationsEnabled`).

Therefore this result is classified as **credential-class mismatch**, not quota exhaustion and not a ReleaseProof semantic-mechanism failure.

## Corrective action

The acceptance harness now requires two distinct server-side secrets before making any provider call:

- `NUTRIENT_API_KEY` - Processor
- `NUTRIENT_DATA_EXTRACTION_API_KEY` - Data Extraction

A corrected hosted run must not start until both secrets are present. The Data Extraction key must come from the same Nutrient organization that received the event credits. Secrets must never be committed or pasted into public artifacts.

## Claim boundary

This run proves real hosted Processor canonicalization on the refactored path and proves that Data Extraction was reached and rejected the wrong credential class. It does **not** prove hosted Data Extraction success, page-level hosted evidence, hosted differential reverification, signing, or end-to-end DWS-native v2 PASS.
