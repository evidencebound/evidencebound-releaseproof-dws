# DWS-Native Semantic Reverification Design

## Goal

Refactor ReleaseProof so Nutrient DWS owns document processing primitives while ReleaseProof owns the approval lifecycle that Nutrient does not provide: cross-document reconciliation, semantic finding identity, differential invalidation, and review carry-forward after document change.

## External architecture review incorporated

The design implements the concrete recommendations received from Nutrient Solutions Engineering on 2026-08-24:

1. Normalize before extracting. Canonical document preparation uses DWS Processor capabilities before schema extraction.
2. Do not diff raw extraction payloads. Bind review continuity to a small normalized finding key: logical document, page, field path, normalized value, and bounding box within an explicit tolerance.
3. Keep cryptographic integrity separate from semantic identity. Whole-document hashes remain provenance/integrity evidence, while page-level hashes localize the blast radius.
4. Use DWS Data Extraction grounding rather than a custom grounding engine. Preserve page reference, bounds, confidence, reading order, and source evidence when supplied by DWS.
5. Use DWS Viewer primitives for the human review projection: finding annotation, reviewer-specific review layer/comment, and a named approved layer/state.
6. Do not reimplement OCR, flattening, splitting/page selection, redaction, or schema generation. Processor and Studio remain the owners of those functions.
7. Provide a Processor digital-signature sealing adapter for a release artifact instead of claiming that a plain JSON hash is equivalent to a standard signed artifact.

## Product boundary

Nutrient establishes source-grounded document evidence and provides the document review primitives.

ReleaseProof determines whether historical human authority over a finding remains valid after the underlying evidence changes.

The ReleaseProof-owned mechanism is:

`canonical DWS evidence -> cross-document finding -> human authority binding -> document revision -> semantic evidence equivalence -> preserve or invalidate review -> mint current release state`

## Data model

### Integrity

`DocumentRevision` integrity remains represented by the source/canonical document SHA-256 and provider receipt SHA-256.

Each grounded field also carries a `page_sha256`. In controlled fixtures this is a deterministic page-evidence digest. In the native hosted path it can be populated from DWS Processor page-isolation output, so a changed page does not imply every page changed.

Page hashes are integrity/provenance signals. They are not used as the sole semantic review identity.

### Semantic evidence identity

Introduce a compact immutable `EvidenceIdentity`:

- `document_id`
- `page`
- `field_path`
- `normalized_value`
- `bounds`

Two identities are equivalent only if:

- document identity matches;
- page matches;
- field path matches;
- normalized value matches;
- every bounding-box coordinate is within the configured tolerance.

Confidence is intentionally excluded from semantic identity. Confidence remains an admissibility/review-routing signal. A minor confidence change does not by itself create a different business fact.

### Stable finding identity

`finding_id` identifies the logical issue and must not depend on evidence bytes or extracted values. It is derived from rule, field, and the logical documents participating in the finding.

`finding_binding` remains a deterministic audit digest of the current semantic evidence identities. Review validity does not rely on string equality of that digest; it uses structured semantic equivalence with the bounding-box tolerance.

### Human review authority

A `HumanReview` stores:

- stable finding ID;
- audit binding digest;
- exact semantic evidence identities reviewed;
- reviewer, decision, rationale.

Differential reverification carries a review forward only when the current finding has the same stable identity and an equivalent semantic evidence set.

## Page-level blast radius

`ReverificationResult` reports both changed documents and changed pages. A document can change while a review on an unchanged page remains valid.

This is deliberately narrower than whole-file invalidation. The old manifest never becomes current after a document revision; ReleaseProof always mints a new current manifest and selectively carries only still-grounded review authority.

## DWS-native adapters

### Processor canonicalization

Add a Processor adapter that performs canonical preparation before extraction. The request is explicit and testable and uses Processor actions rather than local PDF manipulation.

The adapter supports:

- OCR action;
- flatten action;
- page isolation through native Processor `parts[].pages` selection for page-level hashing when requested.

No local OCR or PDF split library is added.

### Data Extraction

Add a Data Extraction adapter for `POST /extraction/extract` using an externally supplied JSON Schema. The repository will not pretend a hand-written schema is Studio-generated. A schema source label is carried so production evidence can distinguish `nutrient-studio`, `provided`, and controlled fixtures.

Normalize only documented source-grounding fields that are present. Missing required grounding fails closed.

The existing hosted Processor `json-content` adapter remains for historical acceptance evidence and backwards compatibility, but it is no longer the target architecture for new hosted runs.

### Viewer projection

ReleaseProof does not implement a competing review UI protocol. It emits a deterministic `ViewerReviewProjection` describing:

- bounding-box annotation for each finding;
- reviewer-specific layer ID;
- review comment/decision metadata;
- named approved-state layer.

This is an adapter contract for native DWS Viewer integration, not a custom overlay engine.

### Digital signature sealing

Add a Processor `/sign` client adapter that accepts a PDF release artifact and returns signed PDF bytes. ReleaseProof retains its JSON manifest hash for internal integrity, but documentation must not call the JSON hash a digital signature.

## EvidenceBound Core extraction

Only generic primitives may graduate into EvidenceBound Core:

1. `EvidenceIdentity`: a small typed identity separate from integrity hashes.
2. `evidence_equivalent`: deterministic equivalence policy with explicit tolerances.
3. Stable logical finding/claim identity separated from evidence binding.
4. `AuthorityBinding`: human authority linked to the exact semantic evidence set and policy version.
5. Typed dependency edges such as `grounds`, `reviewed_by`, `governs`, and `authorizes` for correction propagation.
6. Blast-radius calculation from changed evidence dependencies rather than whole-artifact invalidation.

Do not import or reproduce OntoGuard implementation details, proprietary algorithms, ontology schemas, graph semantics, or product claims. No RDF, OWL, SPARQL, graph database, embeddings, or LLM-based semantic matcher is required. ReleaseProof/EvidenceBound uses a small deterministic typed dependency model developed independently for correction propagation and human control.

## Failure semantics

- Missing grounding: `BLOCKED` or parse failure, never guessed.
- Malformed page reference/bounds/confidence: fail closed.
- Same finding, non-equivalent evidence: prior review invalidated.
- Finding disappears: prior review becomes non-applicable and is not carried forward.
- New finding: no inherited review.
- Manifest tamper: `BLOCKED`.
- Provider integration not live-tested: label `UNVERIFIED`, never `PASS`.
- Viewer/signing adapters implemented but not run with hosted credentials: `UNRUN` until verified.

## Acceptance tests

1. A whole-document byte revision with equivalent normalized finding evidence preserves the review into a new manifest.
2. Bounding-box movement within tolerance preserves review; movement outside tolerance invalidates it.
3. Value normalization preserves semantically equivalent values but a material value change invalidates review.
4. A page-7 change does not invalidate a finding grounded only on unchanged page 2.
5. `finding_id` remains stable across evidence revisions for the same logical issue.
6. Processor canonicalization request uses native OCR/flatten actions.
7. Processor page-isolation request uses native `parts[].pages`, not a local splitter.
8. Data Extraction request uses `/extraction/extract` and an externally supplied schema.
9. Data Extraction normalization preserves DWS page/bounds/confidence/source evidence and fails closed when grounding is absent.
10. Viewer projection maps a finding to annotation, reviewer layer/comment, and approved layer without inventing a second review storage model.
11. `/sign` adapter uses Nutrient Processor signing and does not expose secrets.
12. Existing controlled demo and historical hosted evidence remain truthfully distinguished.
