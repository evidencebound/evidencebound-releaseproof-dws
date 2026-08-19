# ReleaseProof — Devpost Final Submission Checklist

Snapshot: 2026-08-19

## Competition

DevNetwork [API + Cloud + AI] Hackathon 2026

- Submission deadline: **2026-09-03 10:00 PDT / 17:00 UTC**.
- Current overall judging criteria: **Progress / Concept / Feasibility**.
- Video is required by the current submission form.
- Current form also requires a **downloadable backup URL for the original demo MP4** (for example Google Drive, Dropbox, or OneDrive) so organizers can create their Top 5 event video.

## Canonical project identity

**Project:** ReleaseProof

**Pitch:** When a document packet changes, ReleaseProof reprocesses the current evidence and preserves a human exception only if the exact source-grounded finding binding still reproduces.

**Public code:** `https://github.com/moneyparking/evidencebound-releaseproof-dws`

**Public judge evidence URL:** `https://evidencebound-releaseproof-dws.vercel.app`

## Submission truth to preserve

### Progress

Use only verified evidence:

- public repository and Apache-2.0 license;
- Python 3.11 / 3.12 / 3.13 public CI;
- **34/34 tests PASS per Python lane** on the accepted production-evidence revision;
- real hosted Nutrient Processor `/build` execution on three generated PDFs;
- grounded page / bbox / confidence / evidence-slice receipts;
- current release manifest generated from hosted output;
- real cross-document mismatch surfaced as `REVIEW_REQUIRED`;
- public Vercel judge surface READY and accepted.

### Concept

Lead with **Differential Reverification**, not generic provenance:

> A changed document should not automatically erase all human review, and an old approval should not automatically survive. Reprocess the current packet, remint the current manifest, and preserve only the prior review whose exact source-grounded finding binding still reproduces.

Do not claim that provenance graphs, version-aware approvals, or dependency invalidation were invented here.

### Feasibility

Credible startup/company path:

- document-driven operational approvals in trade, procurement, compliance, finance operations, insurance, and other review-heavy workflows;
- DWS performs the core document extraction operation;
- deterministic reconciliation and release predicates sit downstream;
- human review is scoped to evidence and can be replayed/audited;
- customer reviewer-time savings remain a hypothesis until field-tested.

Do not claim customer adoption or measured productivity savings.

## Canonical hosted Nutrient proof

- workflow run: `32215337912`
- commit: `d885ed31ebb8cc9449c450b0334c630c3b11f656`
- artifact: `9352133498`
- artifact digest: `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`
- release manifest: `a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc`
- hosted core DWS: **PASS**
- deterministic Differential Reverification: **PASS**
- hosted Differential Reverification rerun: **NON-BLOCKING LIMITATION — QUOTA_402**

Do not buy a paid Nutrient plan solely to remove the optional hosted differential limitation. If event credits are topped up, the existing acceptance harness can be rerun without changing the evidence semantics.

## Canonical public deployment

- project: `evidencebound-releaseproof-dws`
- project ID: `prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`
- production URL: `https://evidencebound-releaseproof-dws.vercel.app`
- accepted production revision: `dpl_DgptupzTPrqx9HsySqWtwenmUNoA`
- `/`: **PASS / HTTP 200**
- `/health`: **PASS / HTTP 200**
- `/api/live-evidence`: **PASS / HTTP 200**
- `/api/evaluation`: **PASS / HTTP 200**
- `/api/demo`: **PASS / HTTP 200**
- runtime application errors during acceptance: **none observed**
- public runtime Nutrient calls: **DISABLED intentionally**
- Nutrient credential stored in Vercel: **NO**

## Video capture path

The final media owner should capture, in this order:

1. one-sentence problem and buyer;
2. public ReleaseProof judge surface;
3. canonical hosted DWS proof / sanitized receipts;
4. page + bbox + confidence grounding;
5. hosted mismatch -> `REVIEW_REQUIRED`;
6. scoped human review;
7. controlled non-material revision -> new manifest with unchanged scoped review preserved;
8. reviewed evidence-slice change -> old review invalidated;
9. startup path and explicit limitations.

Do not present the Vercel evidence surface as a live Nutrient-calling production service. It intentionally exposes retained accepted evidence so judges/crawlers cannot consume the exhausted free quota.

## Owner-only final media/form actions

- [ ] Produce final demo video and make the submitted video accessible as required by the form.
- [ ] Upload the **original MP4** to a downloadable Drive / Dropbox / OneDrive location.
- [ ] Paste that downloadable MP4 URL into the required Devpost backup-video field.
- [ ] Paste the public judge URL.
- [ ] Paste the public GitHub repository URL.
- [ ] Ensure all final text and video claims match `NUTRIENT_JUDGE_PACK.md`, `docs/claims-ledger.md`, and `qa/QA_RECEIPT.json`.
- [ ] Final submission action remains outside the autonomous engineering boundary.

## Decision

**READY** — engineering, hosted core DWS proof, public CI, and public judge deployment are complete. Remaining work is final media/form submission work plus optional non-blocking improvements.
