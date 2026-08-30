# ReleaseProof — Differential Reverification with Nutrient DWS

**One-line pitch:** After a document packet changes, ReleaseProof reprocesses current source-grounded evidence and preserves prior human authority only when the same logical finding is reproduced from semantically equivalent evidence under the exact equivalence policy frozen when that authority was granted; otherwise the old review cannot release the new packet.

## Submission readiness — READY

ReleaseProof is submission-ready for the Nutrient DWS Challenge except for final media/form work. The competition-critical hosted DWS core operation has already executed successfully against the real Nutrient Processor API and is retained as immutable evidence.

The DWS-native refactor is also now partially hosted-tested. Bounded run `33295050008` on 2026-08-30 successfully executed Processor OCR + flatten canonicalization, then reached Data Extraction and received HTTP 403 because the acceptance harness supplied the historical Processor product key to a service that requires a separate Data Extraction product key. This is a real hosted partial result, not `UNRUN` and not a quota-402 result. Canonical page isolation, hosted differential reverification and signing were not reached after the fail-closed stop. See `docs/hosted-v2-acceptance-2026-08-30.md`.

The corrected acceptance path now requires two distinct server-side secrets before any provider call: `NUTRIENT_API_KEY` for Processor and `NUTRIENT_DATA_EXTRACTION_API_KEY` for Data Extraction. No secret values are stored in this repository.

## Product boundary

Nutrient establishes source-grounded document evidence and provides document processing/review primitives.

ReleaseProof owns the layer Nutrient does not provide:

- cross-document reconciliation;
- stable logical finding identity;
- human authority bound to the exact reviewed evidence;
- frozen rules for continued validity of that authority;
- differential reverification after source change;
- selective invalidation and release gating.

Nutrient owns or supplies the document-native primitives ReleaseProof deliberately does not reimplement:

- Processor OCR, flattening, page operations and signing;
- Data Extraction field grounding;
- Studio schema workflows;
- Viewer annotations, comments, review surfaces and layers.

## Frozen Authority Policy

A review is not just `APPROVED`. It carries the exact rules under which that approval may remain applicable after a future document revision.

The current frozen policy is `evidence-equivalence/1` and commits to:

- bbox tolerance;
- normalized-value algorithm version;
- bbox metric version.

The evidence identity also commits to its coordinate space. Native Data Extraction bboxes are associated with the Processor-canonical rendition; legacy/original-rendition coordinates are never compared as if they belonged to that same space.

That policy, the reviewed evidence identities, reviewer, rationale, decision, finding binding and stable finding ID are hashed into an `AuthorityBinding` and serialized in the release manifest. A later runtime therefore cannot silently reinterpret an old approval by changing a default tolerance or normalization rule.

Example: a review granted at bbox tolerance `2.0` does not survive a 4 px evidence movement even if a later runtime is configured with tolerance `10.0`. Unknown policy versions fail closed to `REVIEW_REQUIRED`. Legacy reviews with no recorded policy receive exact historical-binding behavior only; ReleaseProof does not guess what tolerance an old approval meant.

This mechanism supports deterministic replay, provenance and auditability. It is **not**, by itself, a claim of legal non-repudiation, SOC 2 compliance, FDA 21 CFR Part 11 compliance, ISO certification, or any other regulatory certification.

## Evidence identity

ReleaseProof separates semantic identity from cryptographic integrity.

Semantic evidence identity uses:

```text
document_id
+ page
+ field_path
+ normalized_value
+ bbox within the review's frozen tolerance
+ coordinate_space
```

Integrity/provenance additionally retain document and page hashes, provider response receipt digests, confidence, source evidence block IDs and reading-order metadata where available.

Confidence is intentionally not part of semantic identity. It remains an admissibility/review-routing signal. A provider confidence-only change cannot by itself rewrite what evidence a human approved.

## DWS-native processing path

Target path:

```text
source PDF
  -> Nutrient Processor OCR + flatten
  -> canonical PDF
  -> Nutrient Data Extraction with source grounding
  -> canonical page isolation + page SHA-256
  -> ReleaseProof normalized evidence identity
  -> cross-document findings
  -> HumanReview + frozen equivalence policy
  -> AuthorityBinding
  -> Differential Reverification
  -> optional Viewer projection / Processor signature
```

`process_with_native_dws()` derives pages to isolate from the authoritative grounded field metadata, rather than relying on optional top-level page listings. This prevents a grounded field from losing canonical page-hash provenance when the provider response omits a redundant page index list.

## Differential Reverification semantics

After a source change ReleaseProof always mints a new current manifest. The old manifest never becomes current again.

For each prior review:

1. find the current logical finding by stable finding ID;
2. evaluate the current evidence under the **historical review's frozen equivalence policy**;
3. preserve the review only if the same finding remains grounded in equivalent evidence;
4. otherwise invalidate that authority and return the affected release path to `REVIEW_REQUIRED`.

Page-level hashes reduce blast radius. A change on page 7 does not automatically invalidate authority grounded on unchanged page 2.

## Hosted evidence truth

Historical hosted Processor core:

- run `32215337912`: **PASS**;
- real three-document synthetic packet;
- provider-backed extraction produced a Shipment ID disagreement;
- ReleaseProof surfaced `CROSS_DOCUMENT_MISMATCH` and `REVIEW_REQUIRED` rather than guessing through it.

Historical quota-aware differential rerun:

- run `32215515505`: **BLOCKED_QUOTA_402** on the first `/build` request;
- no hosted differential claim is made from that run.

DWS-native v2 hosted attempt:

- run `33295050008`: **FAIL_PARTIAL_HOSTED**;
- Processor OCR + flatten canonicalization: **PASS_HOSTED**;
- Data Extraction: **FAIL_HTTP_403** from wrong product credential class;
- Processor calls: canonicalize `1`, page isolation `0`, sign `0`;
- Data Extraction calls: `1`;
- sanitized artifact id `9727139742`, ZIP SHA-256 `6f9cb20f5439b12a5ee674ca859521f0fac1778563f99c532e2f4d7a466d7986`;
- page isolation, hosted differential reverification and signing: **UNRUN_AFTER_UPSTREAM_FAILURE**.

Controlled tests and public CI continue to prove the semantic mechanism independently of provider availability.

## Public evidence surface

Production evidence surface:

`https://evidencebound-releaseproof-dws.vercel.app`

The public Vercel surface is an evidence and judge surface. Runtime Nutrient calls are disabled there; hosted provider acceptance is proven separately by immutable GitHub Actions runs and artifacts.

## Local development

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q src tests scripts
```

Generate synthetic probe documents:

```bash
python scripts/generate_synthetic_trade_pdfs.py
python scripts/generate_synthetic_revision.py
```

The hosted v2 workflow is intentionally quota-bounded and cannot run from ordinary PR/push activity. It requires a dedicated trigger branch plus marker file and both server-side Nutrient product credentials.

## Security and claim boundaries

- API keys are server-side secrets only.
- Synthetic acceptance documents contain no customer/private data.
- Raw provider payloads are not committed by the hosted v2 receipt path.
- Unsupported historical policy versions fail closed.
- No ontology, RDF/OWL/SPARQL graph database, embedding matcher or LLM is authoritative for evidence equivalence.
- No regulatory certification or legal non-repudiation claim is made.
- The synthetic acceptance-harness review is not a real human-review metric.
- No real reviewer-time savings or market-size metric is claimed without evidence.
