# Vercel Production Evidence — ReleaseProof

Observed and re-accepted 2026-08-24.

## Dedicated project

- Vercel project: `evidencebound-releaseproof-dws`
- Project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`
- Production alias: `https://evidencebound-releaseproof-dws.vercel.app`
- Current accepted deployment: `dpl_7zdyqLmgv4PEyHxUPJkP6Dp3gDhn`
- Immutable deployment URL: `https://evidencebound-releaseproof-9un6wo3iu.vercel.app`
- Deployed Git commit: `bd670240a681ad139921597ba10b534a570c07f4`
- Region: `iad1`
- Framework detected by Vercel: FastAPI
- Deployment state: `READY`

This is a dedicated project. Existing EvidenceBound Vercel projects were not modified.

## Entry-point fix

The first refactor deployment attempt failed before build because `[tool.vercel] entrypoint = "releaseproof.public_app:app"` did not map to a project-root module in the repository's `src/` layout.

The fix is production accepted:

- root `main.py` exposes the existing FastAPI app;
- `[tool.vercel] entrypoint = "main:app"`;
- regression test requires the configured entrypoint to map to a real root module and expose a FastAPI `app`;
- GitHub Actions run `32757860664`: PASS on Python 3.11, 3.12 and 3.13 plus compile/PDF gates;
- fix merge commit: `bd670240a681ad139921597ba10b534a570c07f4`.

## Evidence-surface boundary

The production service is deliberately an **EVIDENCE_SURFACE**. It exposes already-verified hosted DWS receipts and controlled-mechanism results, but it does not contain a runtime endpoint that calls Nutrient. This prevents judges or crawlers from consuming the exhausted Free-plan processing quota.

Executable mechanism source, DWS transport, normalizer, Differential Reverification implementation and tests remain in this public repository.

## Current refactored production acceptance

- Vercel build/deployment state: **PASS / READY**
- production alias: **PASS**
- `/`: **PASS / HTTP 200**
- `/health`: **PASS / HTTP 200**
- `/api/live-evidence`: **PASS / HTTP 200**
- `/api/evaluation`: **PASS / HTTP 200**
- `/api/demo`: **PASS / HTTP 200**
- runtime error clusters on accepted judge paths during acceptance: **PASS / none observed**

The root surface visibly includes the new Frozen Authority Policy section and DWS-native v2 truth boundary. `/health` reports `dws_native_v2_hosted=UNRUN`, so the accepted production revision preserves the distinction between deployed refactor code and unexecuted credentialed provider paths.

## Nutrient quota boundary

ReleaseProof makes no further Nutrient calls from this deployment.

Status remains:

- hosted Nutrient DWS core: **PASS** via GitHub Actions run `32215337912`;
- deterministic Differential Reverification: **PASS**;
- new DWS-native v2 hosted paths: **UNRUN**;
- hosted Differential Reverification rerun: **BLOCKED_QUOTA_402**;
- public refactored judge evidence URL: **PASS**.

No Nutrient API key is required or stored in Vercel for the evidence surface.

See `docs/production-acceptance-2026-08-24.md` and `qa/QA_RECEIPT.json`.
