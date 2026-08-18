# Nutrient DWS Challenge — Submission Handoff

## Identity

**Canonical project name:** ReleaseProof

**One-line pitch:** When a document packet changes, ReleaseProof reprocesses the current evidence and preserves a human exception only if the exact source-grounded finding binding still reproduces.

**Invention:** Differential Reverification with evidence-scoped human review and reminted release manifests.

## Implemented truth

- three-document trade packet workflow;
- Nutrient hosted Processor `/build` transport;
- strict `json-content` / key-value source-grounding normalizer;
- deterministic mismatch/missing/low-confidence findings;
- scoped human review binding;
- full packet/receipt/decision release manifest;
- historical manifest invalidation after source change;
- Differential Reverification that selectively preserves unchanged review evidence;
- controlled evaluation, tests and local judge UI;
- no-key/no-schema fallback behavior fails closed.

## Not yet verified

- real DWS API execution on the competition account;
- DWS Viewer integration;
- public repository CI;
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

Required before sponsor submission claims DWS PASS:

1. provision a user-controlled `NUTRIENT_API_KEY` server-side;
2. use three non-sensitive representative PDFs;
3. run `scripts/run_live_dws_probe.py` with invoice/shipping/certificate;
4. verify every required field has DWS page/bbox/confidence grounding;
5. retain the DWS response hashes and current manifest;
6. modify/revise a real packet document, reprocess it through DWS and verify Differential Reverification behavior;
7. run full tests and public judge smoke from exact pushed commit.

No fixture may substitute for any of these live steps.

## Prize narrative

**Progress:** working control kernel, DWS transport/normalizer, review/reverification and judge UI.

**Concept:** avoids both stale approval reuse and blanket re-review after document revision.

**Feasibility:** API-first wedge for trade/compliance operations; integration and pricing hypotheses are documented but not presented as validated demand.

**Sponsor memory hook:** “After the packet changes, prove which human review is still grounded in the current document — and which one is not.”

## Prior-art boundary

Version-aware approvals, provenance graphs and dependency invalidation already exist. ReleaseProof does not claim to invent them. The competition contribution is the concrete DWS-grounded, evidence-scoped Differential Reverification pipeline and release predicate. No patent novelty claim is made.

## Exact external blockers / owner actions

### Nutrient credential
Owner action: provision a project/user DWS API key through the intended Nutrient account and inject it only as `NUTRIENT_API_KEY` into a networked runtime/CI secret store.

### Public repository
Current GitHub connector cannot create a new repo. Owner action: create a dedicated public `releaseproof`-style repository, then push this source tree as initial history.

### Public deployment
After live DWS PASS, deploy a server-side service where the API key remains secret. Do not expose credential handling to browser code.

## Capture targets

- hero showing `LIVE NUTRIENT DWS` truth state;
- DWS `/build` request/response receipt (sanitized, no credential);
- field citation page/bbox/confidence;
- mismatch/low-confidence review surface;
- human scoped approval;
- non-material revision preserving unchanged review into a **new** manifest;
- material reviewed-slice revision invalidating the old review;
- raw manifest/audit hashes.
