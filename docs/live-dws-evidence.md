# Hosted Nutrient DWS Evidence Ledger

Date: 2026-08-19

This document records provider-backed evidence separately from controlled fixtures. It contains no API key, Authorization header, or extracted private document content.

## Decision

**Hosted Nutrient DWS core operation: PASS.**

**Hosted Differential Reverification rerun: BLOCKED_QUOTA_402.**

The second status does not erase the accepted core run and is not represented as a failed Differential Reverification result because the revised-document mechanism could not be executed after the provider/account began returning HTTP 402.

## Provider schema discovery

Initial hosted run `32214729108` reached `/build` but the strict normalizer rejected the response because the live page object omitted `pageIndex`.

Schema-only run `32214840848` confirmed the live shape without emitting extracted text:

- top-level ordered `pages[]`;
- page keys included `plainText` and `keyValuePairs`;
- key/value pairs retained confidence;
- key/value objects retained content and bbox grounding;
- value objects also exposed a data type.

ReleaseProof adopted a narrow compatibility rule: documented `pageIndex` remains authoritative when present; only an absent index uses deterministic ordered `pages[]` position and the extraction source is explicitly suffixed `ordered-page-position`. Present malformed indices remain fail-closed.

Public regression CI for this change: `32215060009` — PASS on Python 3.11 / 3.12 / 3.13.

## Canonical core hosted run

GitHub Actions run: `32215337912`

Commit: `d885ed31ebb8cc9449c450b0334c630c3b11f656`

Artifact:
- id: `9352133498`
- name: `live-nutrient-dws-acceptance`
- digest: `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`

Observed acceptance gates:

- server-side secret gate: PASS;
- package install: PASS;
- three synthetic PDF generation: PASS;
- no-fallback hosted DWS probe: PASS;
- execution marker `LIVE_NUTRIENT_DWS`: PASS;
- document count = 3: PASS;
- page provenance >= 1 for every retained field: PASS;
- bbox length = 4 for every retained field: PASS;
- normalized confidence in `[0,1]`: PASS;
- evidence-slice digest for every retained field: PASS;
- base artifact upload: PASS.

Current release manifest SHA-256:

`a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc`

DWS response receipt digests:

- invoice: `f7f472032528a8b874e3de2d48344d9274cde6a448f29530e8ac0f12acc8e7c6`
- shipping: `cef24668bba04f610450eb87fdf873bcdcf45b1e6a9b226865857604f608c135`
- certificate: `8d0b635918e4d42a2f85584a51b6ea52c0f36222b73322242d761317e5d3c4ab`

## Real review trigger observed

The generated source packet used the same intended Shipment ID across documents. The hosted extraction returned divergent Shipment ID strings across the three document outputs. ReleaseProof therefore emitted a `CROSS_DOCUMENT_MISMATCH` and the current manifest state was `REVIEW_REQUIRED`.

This is useful judge evidence for the trust primitive: the pipeline did not silently normalize, guess, or release the packet when provider output disagreed across documents. It does **not** establish an error rate for Nutrient and must not be framed as a provider bug benchmark.

## Hosted Differential Reverification attempt

A live harness was added to test the invention beyond connectivity:

1. retain the accepted original DWS evidence;
2. apply a clearly labelled synthetic acceptance-harness review to a review-required finding;
3. create a byte-different but render-equivalent invoice revision by inserting only a PDF comment before EOF;
4. reprocess the revised invoice through hosted DWS;
5. run `differential_reverify()` and measure preserved/invalidated review bindings.

The first implementation redundantly reprocessed the original packet, making seven hosted calls. Run `32215337912` reached HTTP `402` at the revised-document phase after its three core calls had already passed.

The harness was then optimized to reuse the accepted base evidence and make only one additional revised-invoice call. Public CI run `32215419913` passed with 27 tests and the non-material revision checks.

Hosted rerun `32215515505` returned HTTP `402` on the **first** `/build` request; a subsequent schema request also returned `402`. The run never entered Differential Reverification. Further provider calls were stopped to avoid additional quota spend.

Therefore the correct truth state is:

- core hosted DWS: **PASS**;
- controlled Differential Reverification: **PASS**;
- hosted Differential Reverification: **BLOCKED_QUOTA_402**;
- real reviewer-time savings: **UNVERIFIED**.

## Reproduction after quota restoration

Do not modify the mechanism solely to force a positive result. After quota/credits are restored, run `.github/workflows/live-dws.yml` once. The workflow already contains the quota-aware four-call path and publishes a sanitized receipt to issue #3. Preserve a negative result if provider jitter changes the evidence binding.
