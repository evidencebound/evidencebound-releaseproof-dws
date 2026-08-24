# DWS-Native Semantic Reverification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ReleaseProof DWS-native while preserving its unique differential approval invalidation engine.

**Architecture:** Separate semantic evidence identity from cryptographic integrity. Use native Nutrient Processor/Data Extraction/Viewer/signing adapters around ReleaseProof-owned reconciliation, authority binding, and selective invalidation.

**Tech Stack:** Python 3.11+, dataclasses, requests, FastAPI, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-24-dws-native-semantic-reverification-design.md`

## Global Constraints

- No new runtime dependency unless required by a verified Nutrient API contract.
- No local OCR, PDF splitter, ontology engine, graph database, RDF/OWL/SPARQL, embeddings, or LLM semantic matcher.
- Missing provider grounding fails closed.
- Preserve historical hosted Processor evidence truthfully; do not relabel it as Data Extraction acceptance.
- Hosted Viewer, Data Extraction, and signing remain `UNRUN` until actually executed.
- ReleaseProof owns only reconciliation, semantic review continuity, differential invalidation, and approval lifecycle.

---

### Task 1: Semantic identity and review authority

**Files:**
- Modify: `src/releaseproof/model.py`
- Modify: `src/releaseproof/engine.py`
- Test: `tests/test_semantic_reverification.py`

**Interfaces:**
- Produces: `EvidenceIdentity`, `normalize_evidence_value`, `evidence_identity_equivalent`, `evidence_sets_equivalent`, stable `Finding.finding_id`, structured `HumanReview.evidence_identities`.

- [ ] Write tests proving normalized values and bbox tolerance preserve review continuity.
- [ ] Run tests and confirm RED on current implementation.
- [ ] Implement semantic identity and authority binding.
- [ ] Run targeted tests GREEN.

### Task 2: Page-level blast radius

**Files:**
- Modify: `src/releaseproof/model.py`
- Modify: `src/releaseproof/dws.py`
- Modify: `src/releaseproof/engine.py`
- Test: `tests/test_semantic_reverification.py`

**Interfaces:**
- Produces: citation `page_sha256`, `ReverificationResult.changed_pages`.

- [ ] Write test where page 7 changes while a page 2 review survives.
- [ ] Confirm RED.
- [ ] Implement page evidence hashes and changed-page reporting.
- [ ] Confirm GREEN.

### Task 3: Native Processor canonicalization and page isolation

**Files:**
- Modify: `src/releaseproof/dws.py`
- Test: `tests/test_dws_native_pipeline.py`

**Interfaces:**
- Produces: `NutrientProcessorTransport.canonicalize_pdf(...) -> bytes`, `isolate_page(...) -> bytes`.

- [ ] Test exact `/build` request shapes for OCR + flatten and `parts[].pages` isolation.
- [ ] Confirm RED.
- [ ] Implement minimal transport methods with server-side secret handling.
- [ ] Confirm GREEN.

### Task 4: Native Data Extraction grounding

**Files:**
- Modify: `src/releaseproof/dws.py`
- Test: `tests/test_dws_native_pipeline.py`

**Interfaces:**
- Produces: `NutrientDataExtractionTransport.extract(...)`, `normalize_data_extraction(...)`.

- [ ] Test `/extraction/extract` request with externally supplied schema and mode.
- [ ] Test source page/bounds/confidence/source-evidence preservation and fail-closed behavior.
- [ ] Confirm RED.
- [ ] Implement adapter and normalizer without hand-writing a production schema.
- [ ] Confirm GREEN.

### Task 5: Viewer review projection and signing adapter

**Files:**
- Create: `src/releaseproof/viewer.py`
- Modify: `src/releaseproof/dws.py`
- Test: `tests/test_dws_native_pipeline.py`

**Interfaces:**
- Produces: `ViewerReviewProjection`, `project_finding_for_viewer(...)`, `NutrientSigningTransport.sign_pdf(...)`.

- [ ] Test finding projection to bbox annotation, reviewer layer/comment metadata, approved layer.
- [ ] Test `/sign` request contract.
- [ ] Confirm RED.
- [ ] Implement minimal adapters.
- [ ] Confirm GREEN.

### Task 6: Documentation and truth boundary

**Files:**
- Modify: `README.md`
- Modify: `handoff/NUTRIENT_JUDGE_PACK.md`
- Create: `docs/evidencebound-core-transfer.md`

- [ ] Document architecture boundary and Fabio-driven refactor without claiming hosted acceptance for unrun APIs.
- [ ] Document generic EvidenceBound Core candidates and explicit non-use of OntoGuard proprietary mechanisms.

### Task 7: Full verification and release

- [ ] Run full pytest suite on Python CI matrix.
- [ ] Run compileall and existing synthetic PDF gates.
- [ ] Open PR and inspect diff.
- [ ] Require CI PASS before merge.
- [ ] Merge only if checks are green.
- [ ] Verify production judge surface still returns expected public truth states after deployment.
- [ ] Report hosted Data Extraction/Viewer/signing as `UNRUN` unless a credentialed acceptance run is actually completed.
