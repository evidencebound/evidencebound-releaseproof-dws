# ReleaseProof — Differential Reverification with Nutrient DWS

**One-line pitch:** After a document packet changes, ReleaseProof reprocesses the current evidence and preserves a prior human exception only when the exact document-scoped source-grounded finding binding still reproduces; otherwise the old review cannot release the new packet.

## Judge path

```bash
python -m pip install -e '.[dev]' --no-build-isolation
PYTHONPATH=src pytest
PYTHONPATH=src uvicorn releaseproof.api:app --host 127.0.0.1 --port 8080
```

The deterministic path demonstrates:

- initial reconciliation -> `REVIEW_REQUIRED`;
- scoped human review -> `VERIFIED`;
- non-material file revision -> new manifest while an unchanged scoped review is preserved;
- change to the reviewed evidence slice -> review invalidated and current packet returns to `REVIEW_REQUIRED`.

Controlled fixtures are explicitly labelled `controlled-fixture:nutrient-shaped` and are never presented as live DWS execution.

## Nutrient DWS core operation — LIVE PASS

`NutrientDwsTransport` uses the hosted Processor `/build` path with multipart PDF input and `json-content` / `keyValuePairs: true`. ReleaseProof requires document identity, response receipt hash, field value, page provenance, confidence and bbox grounding before a DWS result can enter a release manifest.

Hosted acceptance on 2026-08-19 processed a three-document synthetic trade packet through the real Nutrient endpoint with no fixture fallback. The canonical evidence run is GitHub Actions `32215337912` at commit `d885ed31ebb8cc9449c450b0334c630c3b11f656`:

- server-side secret gate: **PASS**;
- hosted `/build` connectivity: **PASS**;
- three DWS document operations: **PASS**;
- source-grounding verification for page / bbox / confidence / evidence-slice digest: **PASS**;
- sanitized artifact upload: **PASS**;
- resulting release state: `REVIEW_REQUIRED` because the real extraction produced a cross-document Shipment ID disagreement, which ReleaseProof surfaced rather than silently releasing.

The live provider response omitted the documented `pageIndex` field while retaining an ordered `pages[]` array and grounded key/value boxes. ReleaseProof now uses ordered page position only when `pageIndex` is absent and labels that provenance path `ordered-page-position`; a present malformed page index still fails closed.

## Differential Reverification evidence boundary

The retained deterministic evaluation verifies the mechanism: a whole-file non-material revision causes a blanket-version baseline to preserve `0/1` prior reviews while Differential Reverification preserves `1/1`; changing the reviewed evidence slice preserves `0/1` and requires review again.

A hosted Differential Reverification acceptance harness was also implemented. Its first run redundantly consumed seven DWS operations and hit HTTP `402` on the revised-document request. The harness was reduced to four total hosted calls and passed public CI, but the account subsequently returned HTTP `402` on the first `/build` request. Therefore:

- deterministic Differential Reverification: **PASS**;
- hosted core DWS integration: **PASS**;
- hosted Differential Reverification rerun: **BLOCKED_QUOTA_402**;
- no claim is made that the hosted differential proof passed.

No further DWS calls should be made until account quota/credits are restored.

## Public verification

- public repository: **PASS**;
- Python 3.11 / 3.12 / 3.13 GitHub Actions: **PASS**;
- current deterministic suite: **27 tests PASS**;
- compile gate: **PASS**;
- synthetic non-material PDF revision generator: **PASS**;
- hosted Nutrient core DWS acceptance: **PASS**;
- public judge deployment: **BLOCKED / UNVERIFIED**.

See `docs/live-dws-evidence.md`, `docs/claims-ledger.md`, `qa/QA_RECEIPT.json`, and `handoff/NUTRIENT_JUDGE_PACK.md`.
