# ReleaseProof Production Acceptance - 2026-08-30

## Accepted revision

- Vercel project: `evidencebound-releaseproof-dws`
- Project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`
- Team ID: `team_ecsLjL6dYpwD2SVOcXJfta5Q`
- Production deployment: `dpl_8yEDRk4Bwz2meH2vwSzuZTY5UNaM`
- Immutable deployment URL: `https://evidencebound-releaseproof-lj87ka83w.vercel.app`
- Production alias: `https://evidencebound-releaseproof-dws.vercel.app`
- Git commit deployed: `77bda0ba7c15a79ad0c9e6b2e26931c206528504`
- Deployment state: `READY`
- Target: `production`
- Framework: FastAPI
- Region: `iad1`
- Source: Vercel CLI

## Acceptance checks

| Check | Status | Evidence |
|---|---|---|
| deployment state | PASS | Vercel reports `READY` and alias assignment succeeded |
| deployed commit | PASS | deployment metadata reports `77bda0ba7c15a79ad0c9e6b2e26931c206528504` |
| `/` | PASS | HTTP 200; judge surface visibly reports `DWS-NATIVE V2 CORE · HOSTED PASS` |
| `/health` | PASS | HTTP 200; `dws_native_v2_core_hosted=PASS`, `live_differential_reverification=PASS_HOSTED`, signing `FAIL_HTTP_400`, Viewer `UNRUN` |
| `/api/v2-evidence` | PASS | HTTP 200; current hosted v2 receipt exposes run `33296171708` and accepted gates |
| `/api/live-evidence` | PASS | HTTP 200; backward-compatible historical Processor receipt retained |
| `/api/demo` | PASS | HTTP 200; controlled mechanism remains executable |
| `/api/evaluation` | PASS | HTTP 200; controlled reuse/invalidation metrics remain available |
| runtime errors on accepted judge paths | PASS | no runtime error clusters observed in the acceptance window |

## Current production truth

- historical hosted Processor core: **PASS**;
- DWS-native v2 core: **PASS_HOSTED**;
- hosted Differential Reverification: **PASS_HOSTED**;
- non-material authority preservation: **PASS_HOSTED**;
- material authority invalidation: **PASS_HOSTED**;
- Processor `/sign`: **FAIL_HTTP_400**;
- hosted Viewer review execution: **UNRUN**.

The signing limitation is independent of the accepted core path. Hosted run `33296171708` reached `/sign` only after Processor canonicalization, Data Extraction, canonical page grounding/hashes, non-material authority preservation and material authority invalidation assertions had passed. Isolated sign probe run `33296422243` reproduced HTTP 400 after Processor normalization.

## Public-surface boundary

The Vercel service is an evidence surface. It performs no live Nutrient calls from public judge routes and exposes no provider credentials. Provider-backed evidence is retained as sanitized immutable receipts from GitHub Actions.

The historical 2026-08-24 production acceptance remains valid for its then-current revision but is superseded for current judge-surface status by this acceptance.
