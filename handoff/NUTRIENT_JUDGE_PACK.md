# Nutrient DWS Challenge — Submission Handoff

## Identity

**Canonical project name:** ReleaseProof

**One-line pitch:** When a document packet changes, ReleaseProof reprocesses the current evidence and preserves a human exception only if the exact source-grounded finding binding still reproduces.

**Invention:** Differential Reverification with evidence-scoped human review and reminted release manifests.

## Implemented and verified truth

- dedicated public competition repository;
- three-document trade packet workflow;
- Nutrient hosted Processor `/build` transport;
- strict `json-content` / key-value source-grounding normalizer;
- compatibility with the observed hosted response that omitted documented `pageIndex`, using explicit ordered-page-position provenance rather than silent guessing;
- deterministic mismatch/missing/low-confidence findings;
- scoped human review binding;
- full packet/receipt/decision release manifest;
- historical manifest invalidation after source change;
- Differential Reverification selectively preserves unchanged review evidence in the controlled mechanism;
- 27 deterministic tests + compile gate;
- public GitHub Actions matrix on Python 3.11 / 3.12 / 3.13;
- live hosted DWS processing of three generated PDFs with no fixture fallback;
- live field-level page/bbox/confidence/evidence-slice verification;
- live current manifest and DWS response receipt hashes;
- real live `CROSS_DOCUMENT_MISMATCH` routed to `REVIEW_REQUIRED` rather than silently released.

## Canonical hosted DWS proof

GitHub Actions run: `32215337912`

Commit: `d885ed31ebb8cc9449c450b0334c630c3b11f656`

Artifact:
- id: `9352133498`
- digest: `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`

Release manifest:
`a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc`

DWS receipt hashes:
- invoice: `f7f472032528a8b874e3de2d48344d9274cde6a448f29530e8ac0f12acc8e7c6`
- shipping: `cef24668bba04f610450eb87fdf873bcdcf45b1e6a9b226865857604f608c135`
- certificate: `8d0b635918e4d42a2f85584a51b6ea52c0f36222b73322242d761317e5d3c4ab`

The generated source packet intended the same Shipment ID across documents. Hosted extraction returned divergent Shipment ID strings. ReleaseProof detected the disagreement and generated `REVIEW_REQUIRED`. Treat this as evidence of fail-closed reconciliation, **not** as a measured Nutrient error-rate or provider-bug claim.

## Differential Reverification proof

### Controlled mechanism — PASS

Retained evaluation:
- prior reviews: 1;
- blanket whole-file baseline preserves 0/1 after a non-material file revision;
- Differential Reverification preserves 1/1 when the reviewed finding binding is unchanged;
- when the reviewed evidence slice changes, 0/1 is preserved and current state returns to `REVIEW_REQUIRED`.

### Hosted DWS differential run — BLOCKED_QUOTA_402

A hosted acceptance harness creates a byte-different but render-equivalent invoice revision, uses a clearly labelled synthetic acceptance-harness review, reprocesses the revised invoice through DWS, and runs `differential_reverify()`.

The first implementation redundantly reprocessed the base packet and reached HTTP `402` before the revised-document result. It was redesigned to reuse the accepted base DWS evidence, reducing total hosted calls from seven to four. That quota-aware harness passed public CI in run `32215419913`.

Hosted rerun `32215515505` then received HTTP `402` on the first `/build`; the diagnostic call also returned `402`. No Differential Reverification result was produced. Further provider calls were stopped rather than spending more quota.

Do **not** claim hosted Differential Reverification PASS. The correct distinction is:
- hosted core DWS: **PASS**;
- deterministic Differential Reverification: **PASS**;
- hosted differential proof: **BLOCKED_QUOTA_402**.

## Prize narrative

**Progress:** public source, passing public CI, live DWS-backed document processing, real source-grounding receipts, release-manifest generation, deterministic review/reverification mechanism and judge UI.

**Concept:** stale approvals should not survive merely because a file/version identifier changed or remained familiar. ReleaseProof binds review to the exact source-grounded finding evidence and remints the decision state for the current packet.

**Feasibility:** the hosted Processor integration now works end-to-end on three PDFs. The live disagreement case demonstrates why deterministic cross-document reconciliation plus explicit human review is operationally useful. Customer productivity remains a hypothesis, not a measured claim.

**Sponsor memory hook:** “After the packet changes, prove which human review is still grounded in the current document — and which one is not.”

## Prior-art boundary

Version-aware approvals, provenance graphs and dependency invalidation already exist. ReleaseProof does not claim to invent them. The competition contribution is the concrete DWS-grounded, evidence-scoped Differential Reverification pipeline and release predicate. No patent novelty claim is made.

## Remaining blockers

### Public judge deployment — BLOCKED
Deploy the exact accepted source behind a server-side secret boundary and run the full public smoke path. Never expose `NUTRIENT_API_KEY` to browser code.

### Hosted Differential Reverification rerun — BLOCKED_QUOTA_402
After Nutrient quota/credits are restored, run the existing `live-nutrient-dws` workflow once. Do not change evidence-binding semantics to force a positive result; preserve provider-jitter negative results if observed.

### DWS Viewer — OPTIONAL / UNRUN
Evaluate only if it materially strengthens the human review experience without displacing Processor as the core document operation.

### Real user metrics — UNVERIFIED
No claim of measured reviewer-time savings or customer adoption is made.

## Capture targets

- public judge hero showing live/fixture truth state;
- sanitized hosted DWS run/receipt evidence;
- page/bbox/confidence grounding;
- live mismatch -> `REVIEW_REQUIRED`;
- scoped approval UI;
- controlled non-material revision preserving unchanged review into a **new** manifest;
- material reviewed-slice revision invalidating the old review;
- live manifest/audit hashes;
- explicit quota-boundary disclosure for hosted Differential Reverification.

See `docs/live-dws-evidence.md` and `qa/QA_RECEIPT.json`.
