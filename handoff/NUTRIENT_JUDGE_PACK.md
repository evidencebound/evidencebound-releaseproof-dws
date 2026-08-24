# Nutrient DWS Challenge — Submission Handoff

## Identity

**Canonical project name:** ReleaseProof

**One-line pitch:** When a document packet changes, ReleaseProof reprocesses current source-grounded evidence and preserves human authority only if the same logical finding still reproduces from semantically equivalent evidence.

**Invention:** Differential Reverification with evidence-scoped human authority and reminted current release state.

**Submission status:** **READY** except final video / Devpost form work. No paid Nutrient plan is required for the already accepted competition path.

## Product boundary

Nutrient owns document primitives: canonical document processing, OCR/flatten/page operations, structured extraction and source grounding, Viewer review primitives, and signed PDF tooling.

ReleaseProof owns:

- cross-document reconciliation;
- stable logical finding identity;
- human authority binding;
- Differential Reverification;
- selective invalidation after evidence change;
- approval lifecycle and current release state.

The current semantic review key is deliberately small and auditable:

`logical document + page + field path + normalized value + bbox within tolerance`

Cryptographic hashes remain integrity/provenance signals, not semantic identity.

## DWS-native refactor — implemented and CI verified

The 2026-08-24 refactor incorporates the platform architecture review received from Nutrient while preserving the ReleaseProof-owned mechanism.

Implemented:

- stable finding IDs independent of extraction bytes;
- structured semantic `EvidenceIdentity` separate from SHA-256 integrity;
- bbox-tolerant evidence equivalence;
- confidence kept as review/admissibility metadata rather than semantic identity;
- page-level digests and changed-page blast-radius reporting;
- Processor-native OCR + flatten canonicalization adapter;
- Processor-native page isolation adapter using `parts[].pages`;
- Data Extraction `/extraction/extract` transport using externally supplied JSON Schema and `citationsEnabled: true`;
- Data Extraction normalizer for provider `pageIndex`, `pageNumber`, bbox, confidence, `source_bboxes`, and optional reading order;
- Studio/external schema truth boundary through `NUTRIENT_EXTRACTION_SCHEMA_JSON` rather than claiming a repository schema was Studio-generated;
- Viewer review projection to finding annotation, reviewer-specific layer/comment, and named approved layer;
- Processor `/sign` adapter for a standard signed PDF release artifact path;
- no local OCR, PDF splitter, ontology engine, graph database, embeddings, or LLM evidence matcher.

Verification at the refactor code head:

- Python 3.11: **49/49 PASS**;
- Python 3.12: **49/49 PASS**;
- Python 3.13: **49/49 PASS**;
- compileall: **PASS**;
- synthetic three-PDF generation/validation: **PASS**;
- render-equivalent non-material revision gate: **PASS**;
- source snapshot artifact: **PASS**.

The documentation commits after that code head require one final CI run before merge.

## Hosted truth boundary

### Historical hosted Processor core — LIVE PASS

GitHub Actions run: `32215337912`

Commit: `d885ed31ebb8cc9449c450b0334c630c3b11f656`

Artifact:
- id: `9352133498`;
- digest: `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`.

Release manifest:
`a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc`

DWS receipt hashes:
- invoice: `f7f472032528a8b874e3de2d48344d9274cde6a448f29530e8ac0f12acc8e7c6`;
- shipping: `cef24668bba04f610450eb87fdf873bcdcf45b1e6a9b226865857604f608c135`;
- certificate: `8d0b635918e4d42a2f85584a51b6ea52c0f36222b73322242d761317e5d3c4ab`.

The generated packet intended the same Shipment ID across documents. Hosted Processor extraction returned divergent Shipment ID strings. ReleaseProof detected the disagreement and returned `REVIEW_REQUIRED`. This is evidence of fail-closed reconciliation, not a measured Nutrient error-rate claim.

The live Processor response omitted documented `pageIndex` while retaining ordered `pages[]` plus grounded key/value boxes. The historical compatibility path uses ordered page position only when `pageIndex` is absent and labels that provenance explicitly.

This accepted historical run is **not** relabelled as Data Extraction API acceptance.

### New v2 hosted paths

- Processor OCR/flatten canonicalization: **UNRUN**;
- Processor page isolation for canonical per-page hash: **UNRUN**;
- Data Extraction `/extraction/extract`: **UNRUN**;
- Viewer review flow: **UNRUN**;
- Processor `/sign`: **UNRUN**.

All are implemented as tested contracts, but no hosted PASS is claimed until a credentialed acceptance run occurs.

## Differential Reverification proof

### Controlled mechanism — PASS

The controlled suite now verifies:

- blanket whole-file baseline preserves `0/1` old review after a non-material file revision;
- Differential Reverification preserves `1/1` when semantic evidence identity still reproduces;
- confidence-only drift does not incorrectly become a semantic change;
- bbox drift within tolerance preserves review;
- bbox drift outside tolerance invalidates review;
- a material normalized-value change invalidates prior review;
- a page-7 integrity change can leave a page-2 review valid;
- current state is always reminted into a new manifest after source revision.

### Hosted Differential Reverification rerun — NON-BLOCKING LIMITATION: QUOTA_402

The earlier hosted differential harness was optimized from seven calls to four by reusing accepted base evidence. A subsequent run received HTTP `402` on the first Processor `/build` request. Therefore:

- hosted core Processor integration: **PASS**;
- controlled Differential Reverification: **PASS**;
- hosted Differential Reverification proof: **NON-BLOCKING LIMITATION — QUOTA_402**.

Do not claim hosted Differential Reverification PASS unless a new hosted run actually succeeds.

## Public judge URL

`https://evidencebound-releaseproof-dws.vercel.app`

The deployed service is intentionally an `EVIDENCE_SURFACE`. It exposes retained live receipts and controlled mechanism evidence without exposing Nutrient credentials or consuming provider quota from judge/browser traffic.

Previously accepted production revision:
`dpl_DgptupzTPrqx9HsySqWtwenmUNoA`

Previously accepted endpoints:

- `/`: **HTTP 200 PASS**;
- `/health`: **HTTP 200 PASS**;
- `/api/live-evidence`: **HTTP 200 PASS**;
- `/api/evaluation`: **HTTP 200 PASS**;
- `/api/demo`: **HTTP 200 PASS**.

This production evidence is historical until the refactor is merged and a new production acceptance is recorded.

## Prize narrative

**Progress:** public source, live DWS-backed historical processing evidence, source-grounded receipts, deterministic semantic review continuity, passing public CI, and a live evidence surface.

**Concept:** a human approval should neither survive blindly because a document is “the same file” nor be reset blindly because any byte changed. ReleaseProof separates integrity from semantic review identity and invalidates only authority whose grounded evidence no longer reproduces.

**Feasibility:** the core hosted Processor integration already works end to end. The DWS-native v2 architecture removes duplicated platform work and keeps the ReleaseProof-owned layer focused on cross-document reconciliation, human authority, and differential invalidation.

**Sponsor memory hook:** “After the packet changes, prove which human review is still grounded in current evidence, and which one is not.”

## Prior-art and IP boundary

Version-aware approvals, provenance graphs, dependency invalidation, ontologies and knowledge graphs already exist. ReleaseProof does not claim to invent them.

The competition contribution is the concrete DWS-grounded Differential Reverification mechanism and approval lifecycle. The repository does not copy OntoGuard ontology schemas, proprietary algorithms, policy language or implementation details. EvidenceBound transfer candidates are independently defined typed evidence/authority primitives and deterministic dependency semantics only.

No patent novelty claim is made.

## Current limitations

- hosted Differential Reverification rerun: **QUOTA_402**;
- new v2 Data Extraction hosted acceptance: **UNRUN**;
- Viewer hosted review integration: **UNRUN**;
- `/sign` hosted acceptance: **UNRUN**;
- real reviewer-time/customer metrics: **UNVERIFIED**.

## Capture targets

- public judge hero;
- retained hosted DWS run/receipt evidence;
- real hosted mismatch -> `REVIEW_REQUIRED`;
- semantic review key visualization: page + field path + normalized value + bbox tolerance;
- non-material revision preserving review into a new manifest;
- material evidence revision invalidating old authority;
- page-local blast-radius case;
- clear boundary between historical hosted PASS and new v2 UNRUN integrations.

See `README.md`, `docs/live-dws-evidence.md`, `docs/vercel-production-evidence.md`, `docs/evidencebound-core-transfer.md`, and `qa/QA_RECEIPT.json`.
