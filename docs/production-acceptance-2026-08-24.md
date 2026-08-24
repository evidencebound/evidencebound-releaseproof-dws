# ReleaseProof Production Acceptance — 2026-08-24

## Accepted revision

- Vercel project: `evidencebound-releaseproof-dws`
- Project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`
- Production deployment: `dpl_7zdyqLmgv4PEyHxUPJkP6Dp3gDhn`
- Immutable deployment URL: `https://evidencebound-releaseproof-9un6wo3iu.vercel.app`
- Production alias: `https://evidencebound-releaseproof-dws.vercel.app`
- Git commit deployed: `bd670240a681ad139921597ba10b534a570c07f4`
- Deployment state: `READY`
- Target: `production`
- Framework: FastAPI
- Region: `iad1`

## Acceptance checks

| Check | Status | Evidence |
|---|---|---|
| deployment state | PASS | Vercel reports `READY` |
| production alias | PASS | alias points to accepted revision |
| `/` | PASS | HTTP 200, refactored judge surface renders Frozen Authority Policy and DWS-native v2 boundary |
| `/health` | PASS | HTTP 200, includes `dws_native_v2_hosted=UNRUN` and quota boundary |
| `/api/demo` | PASS | HTTP 200, controlled Differential Reverification output returned |
| `/api/evaluation` | PASS | HTTP 200, controlled review preservation/invalidation metrics returned |
| `/api/live-evidence` | PASS | HTTP 200, canonical hosted Nutrient evidence retained |
| runtime errors on accepted judge paths | PASS | no runtime error clusters observed during acceptance window |

## Truth boundary

This acceptance proves that the refactored public evidence surface is deployed and serving the intended judge workflow.

It does **not** convert the new credentialed DWS-native v2 provider paths into hosted PASS. The following remain `UNRUN` until a real Nutrient-hosted acceptance succeeds:

- Processor OCR/flatten canonicalization;
- Processor page isolation for canonical page hashes;
- Data Extraction `/extraction/extract`;
- DWS Viewer review flow;
- Processor `/sign`.

The historical hosted Processor core remains PASS via GitHub Actions run `32215337912`. Hosted Differential Reverification remains `BLOCKED_QUOTA_402`.

The public Vercel surface performs no runtime Nutrient calls and requires no Nutrient secret. This preserves the exhausted provider quota while exposing retained live evidence and controlled mechanism results to judges.
