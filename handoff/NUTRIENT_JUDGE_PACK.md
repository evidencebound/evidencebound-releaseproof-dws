# Nutrient DWS Challenge — Submission Handoff

## Identity

**Canonical project name:** ReleaseProof

**One-line pitch:** When a document packet changes, ReleaseProof reprocesses the current evidence and preserves a human exception only if the exact source-grounded finding binding still reproduces.

**Invention:** Differential Reverification with evidence-scoped human review and reminted release manifests.

## Implemented truth

- dedicated public competition repository exists;
- three-document trade packet workflow;
- Nutrient hosted Processor `/build` transport;
- strict `json-content` / key-value source-grounding normalizer;
- deterministic mismatch/missing/low-confidence findings;
- scoped human review binding;
- full packet/receipt/decision release manifest;
- historical manifest invalidation after source change;
- Differential Reverification selectively preserves unchanged review evidence;
- controlled evaluation, tests and local judge UI;
- no-key/no-schema fallback behavior fails closed;
- public GitHub Actions matrix passes after resolving current Starlette TestClient dependency drift.

## Not yet verified

- successful real DWS API response on three representative PDFs;
- DWS Viewer integration;
- public judge deployment;
- real user/customer metrics.

## Controlled proof

Retained fixture:
- prior reviews: 1;
- blanket whole-file baseline preserves 0/1 after a non-material file revision;
- Differential Reverification preserves 1/1 when the reviewed finding binding is unchanged;
- when the reviewed evidence slice changes, 0/1 is preserved and current state returns to `REVIEW_REQUIRED`.

This is mechanism evidence only.

## Live DWS acceptance gate

A user-controlled DWS key was supplied transiently on 2026-08-18, but the current sandbox could not resolve `api.nutrient.io`; no HTTP response was obtained and the key was not persisted. Before sponsor submission claims DWS PASS:

1. inject the credential only as server-side `NUTRIENT_API_KEY` in a networked runtime/secret store;
2. use three non-sensitive representative PDFs;
3. run `scripts/run_live_dws_probe.py` with invoice/shipping/certificate;
4. verify every required field has DWS page/bbox/confidence grounding;
5. retain sanitized DWS response hashes and the current manifest;
6. revise a real packet document, reprocess through DWS and verify Differential Reverification behavior;
7. run public judge smoke from the exact deployed commit.

No fixture may substitute for these live steps.

## Prize narrative

**Progress:** public source, passing public CI, working control kernel, DWS transport/normalizer, review/reverification and judge UI.

**Concept:** avoids both stale approval reuse and blanket re-review after document revision.

**Feasibility:** API-first wedge for trade/compliance operations; integration and pricing hypotheses are documented but not presented as validated demand.

**Sponsor memory hook:** “After the packet changes, prove which human review is still grounded in the current document — and which one is not.”

## Prior-art boundary

Version-aware approvals, provenance graphs and dependency invalidation already exist. ReleaseProof does not claim to invent them. The competition contribution is the concrete DWS-grounded, evidence-scoped Differential Reverification pipeline and release predicate. No patent novelty claim is made.

## Remaining external blockers / owner actions

### Live Nutrient execution — BLOCKED by current execution network
Run the no-fallback live probe in a networked environment with the server-side key. Do not commit or expose the credential.

### Public deployment — BLOCKED
After live DWS PASS, deploy a server-side service where the API key remains secret and smoke-test the exact deployed commit.

### DWS Viewer — OPTIONAL / UNRUN
Evaluate only if it materially strengthens the human review experience without displacing Processor as the core document operation.

## Public CI evidence

- PR CI head: `161c62559c6737bacc375e4cd952c2f333f1dec2`
- GitHub Actions run: `32179703793`
- conclusion: `success`

## Capture targets

- hero showing the truthful live DWS state;
- DWS `/build` request/response receipt (sanitized, no credential);
- field citation page/bbox/confidence;
- mismatch/low-confidence review surface;
- human scoped approval;
- non-material revision preserving unchanged review into a **new** manifest;
- material reviewed-slice revision invalidating the old review;
- raw manifest/audit hashes.
