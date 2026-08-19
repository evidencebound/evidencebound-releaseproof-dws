# ReleaseProof — Differential Reverification with Nutrient DWS

**One-line pitch:** After a document packet changes, ReleaseProof reprocesses the current evidence and preserves a prior human exception only when the exact document-scoped source-grounded finding binding still reproduces; otherwise the old review cannot release the new packet.

## Judge path

Public evidence URL:

`https://evidencebound-releaseproof-dws.vercel.app`

Local executable mechanism:

```bash
python -m pip install -e '.[dev]' --no-build-isolation
PYTHONPATH=src pytest
PYTHONPATH=src uvicorn releaseproof.public_app:app --host 127.0.0.1 --port 8080
```

The public judge surface exposes:

- `/` — truthful judge surface separating hosted and controlled evidence;
- `/health` — machine-readable PASS/BLOCKED states;
- `/api/live-evidence` — sanitized immutable receipt for the accepted hosted DWS run;
- `/api/demo` — controlled mechanism summary;
- `/api/evaluation` — controlled Differential Reverification metrics.

The Vercel service is deliberately labelled `EVIDENCE_SURFACE`. It does **not** call Nutrient from the browser, page load, or any public endpoint. Executable Differential Reverification and DWS integration remain in this repository, while the deployment exposes the accepted receipts and controlled evaluation without allowing judges or crawlers to consume the exhausted Nutrient quota.

The deterministic mechanism demonstrates:

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

A hosted Differential Reverification acceptance harness was also implemented. Its first run redundantly consumed seven DWS operations and hit HTTP `402` on the revised-document request. The harness was reduced to four total hosted calls and passed public CI, but the account subsequently returned HTTP `402` on the first `/build` request. The user then received Nutrient's Free-plan quota warning showing two processing credits remaining. Therefore:

- deterministic Differential Reverification: **PASS**;
- hosted core DWS integration: **PASS**;
- hosted Differential Reverification rerun: **BLOCKED_QUOTA_402**;
- no claim is made that the hosted differential proof passed.

No further DWS calls should be made until account quota/credits are restored.

## Production deployment — PASS

Dedicated Vercel project:

- project: `evidencebound-releaseproof-dws`;
- project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`;
- production alias: `https://evidencebound-releaseproof-dws.vercel.app`;
- initial accepted deployment: `dpl_HDEAT39ZTarETnZUX7gTemWCG4to`;
- framework/runtime: FastAPI / Python 3.12;
- build: **PASS**;
- deployment state: **READY**;
- `/`, `/health`, `/api/live-evidence`, `/api/evaluation`, `/api/demo`: **HTTP 200 PASS**;
- runtime application errors during acceptance: **none observed**.

No Nutrient credential is stored in Vercel. The exact deployment evidence surface is retained in `deploy/vercel_evidence_surface.py`; see `docs/vercel-production-evidence.md`.

## Public verification

- public repository: **PASS**;
- Python 3.11 / 3.12 / 3.13 GitHub Actions: **PASS**;
- compile gate: **PASS**;
- controlled Differential Reverification: **PASS**;
- hosted Nutrient core DWS acceptance: **PASS**;
- public judge deployment: **PASS**;
- hosted Differential Reverification: **BLOCKED_QUOTA_402**;
- DWS Viewer: **UNRUN / optional**;
- real reviewer-time or customer metrics: **UNVERIFIED**.

See `docs/live-dws-evidence.md`, `docs/vercel-production-evidence.md`, `docs/claims-ledger.md`, `qa/QA_RECEIPT.json`, and `handoff/NUTRIENT_JUDGE_PACK.md`.
