# Vercel Production Evidence — ReleaseProof

Observed 2026-08-19.

## Dedicated project

- Vercel project: `evidencebound-releaseproof-dws`
- Project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`
- Production alias: `https://evidencebound-releaseproof-dws.vercel.app`
- Initial accepted deployment: `dpl_HDEAT39ZTarETnZUX7gTemWCG4to`
- Region: `iad1`
- Framework detected by Vercel: FastAPI / Python 3.12

This is a dedicated project. Existing EvidenceBound Vercel projects were not modified.

## Evidence-surface boundary

The production service is deliberately an **EVIDENCE_SURFACE**. It exposes already-verified hosted DWS receipts and controlled-mechanism results, but it does not contain a runtime endpoint that calls Nutrient. This prevents judges or crawlers from consuming the exhausted Free-plan processing quota.

Executable mechanism source, DWS transport, normalizer, Differential Reverification implementation and tests remain in this public repository. The deployed source is retained as `deploy/vercel_evidence_surface.py`.

## Production acceptance

Initial deployment build:

- Vercel build: **PASS**
- deployment state: **READY**
- `/`: **PASS / HTTP 200**
- `/health`: **PASS / HTTP 200**
- `/api/live-evidence`: **PASS / HTTP 200**
- `/api/evaluation`: **PASS / HTTP 200**
- `/api/demo`: **PASS / HTTP 200**
- serverless runtime logs for those requests: **PASS**, no application error observed

The first deployment returned 404 for browser favicon requests only. The repository deployment source now includes explicit 204 favicon routes; this is cosmetic and does not affect the accepted judge path.

## Nutrient quota boundary

The user received Nutrient's Free-plan warning with two processing credits remaining after the live acceptance work. Subsequent hosted requests had already returned HTTP 402. ReleaseProof therefore makes no further Nutrient calls from this deployment.

Status remains:

- hosted Nutrient DWS core: **PASS** via GitHub Actions run `32215337912`;
- deterministic Differential Reverification: **PASS**;
- hosted Differential Reverification rerun: **BLOCKED_QUOTA_402**;
- public judge evidence URL: **PASS**.

No API key is required or stored in Vercel for the evidence surface.
