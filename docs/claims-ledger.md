# Claims Ledger

| Claim | Evidence class | Status |
|---|---|---|
| controlled packet reaches `REVIEW_REQUIRED` then `VERIFIED` after scoped review | deterministic fixtures/tests | VERIFIED / public CI |
| non-material whole-file revision creates a new manifest and preserves unchanged review authority | controlled evaluation + parity-locked result | VERIFIED / public CI |
| confidence-only drift does not by itself change semantic evidence identity | regression test | VERIFIED / public CI |
| normalized-value change invalidates prior review authority | controlled evaluation + regression test | VERIFIED / public CI |
| bbox movement within frozen tolerance can preserve review; movement outside invalidates | regression tests | VERIFIED / public CI |
| later runtime bbox defaults cannot reinterpret existing policy-bound authority | frozen-policy regression test | VERIFIED / public CI |
| unsupported equivalence-policy versions fail closed to `REVIEW_REQUIRED` | regression test | VERIFIED / public CI |
| `authority_binding` commits to reviewed evidence and frozen policy and is serialized in the manifest | regression tests | VERIFIED / public CI |
| legacy reviews without frozen policy remain exact-binding only | compatibility tests | VERIFIED / public CI |
| page-level integrity can localize blast radius | page-level regression tests | VERIFIED / public CI |
| Processor-canonical coordinate space is part of evidence identity | coordinate-space regression tests | VERIFIED / public CI |
| bbox from different coordinate spaces cannot silently match | coordinate-space regression tests | VERIFIED / public CI |
| malformed/missing source grounding fails closed | normalizer tests | VERIFIED / public CI |
| hosted Processor canonicalization executes on DWS-native v2 path | run `33296171708` | **PASS_HOSTED** |
| hosted Data Extraction executes on canonical Processor renditions | run `33296171708` | **PASS_HOSTED** |
| hosted Data Extraction returns grounded page/bbox/confidence/source evidence usable by ReleaseProof | run `33296171708` | **PASS_HOSTED** |
| hosted canonical page isolation/hash path executes | run `33296171708` | **PASS_HOSTED** |
| hosted non-material source revision preserves targeted prior authority | run `33296171708` | **PASS_HOSTED** |
| hosted material reviewed evidence change invalidates targeted prior authority | run `33296171708` | **PASS_HOSTED** |
| hosted material change returns current packet to `REVIEW_REQUIRED` | run `33296171708` | **PASS_HOSTED** |
| DWS-native Differential Reverification core executes against real hosted Nutrient services | run `33296171708` | **PASS_HOSTED** |
| Processor `/sign` seals the final release artifact in the current account | runs `33296171708`, `33296422243` | **FAIL_HTTP_400** - not claimed as PASS |
| Viewer finding/review maps to annotation + reviewer layer/comment + approved layer | deterministic projection | VERIFIED / hosted Viewer **UNRUN** |
| production schema was generated/refined in Nutrient Studio | external product step | **UNVERIFIED / UNRUN** |
| historical hosted Processor core processed a three-document synthetic packet | run `32215337912` | VERIFIED |
| historical live output omitted documented `pageIndex`; ordered-position fallback is provenance-labelled and malformed present indices fail closed | historical diagnostic + CI; Nutrient SE feedback | VERIFIED observation |
| real ReleaseProof surfaced a cross-document disagreement instead of silently releasing | historical run `32215337912` | VERIFIED |
| public GitHub CI covers Python 3.11/3.12/3.13 | GitHub Actions | PASS |
| current Vercel surface already exposes the new hosted-v2 status | deployment verification | **STALE / redeploy required** |
| Differential Reverification addresses corrected/re-issued packet workflows | Nutrient Solutions Engineering field feedback | EXTERNAL FIELD OBSERVATION, not market-size claim |
| mechanism reduces real reviewer time | field study | UNVERIFIED |
| mechanism establishes SOC 2/FDA/ISO compliance or legal non-repudiation | broader operational/regulatory assessment | NOT CLAIMED |

## Current hosted proof

The current DWS-native v2 core proof is GitHub Actions run `33296171708`:

- job `99216095769`;
- trigger commit `0a0e3d1d9a38f2ebfe5a50712222741d4930f018`;
- artifact `9727472871`;
- artifact ZIP SHA-256 `fc7b7b9cfc2cee71912e59580f53ada8f03098b8532266f0cbf6507021f3bab2`;
- Processor calls: `canonicalize=5`, `isolate_page=5`, `sign=1`;
- Data Extraction calls: `5`.

The harness reaches `sign_pdf()` only after all core assertions pass. It therefore proves the following before its optional signing failure:

1. Processor OCR/flatten canonicalization;
2. Data Extraction on canonical renditions;
3. grounded field metadata;
4. native page isolation and canonical page hashes;
5. explicit `nutrient-processor-canonical-rendition/1` coordinate space;
6. intentional cross-document mismatch;
7. reviewed baseline `VERIFIED` state using a clearly labelled synthetic acceptance-harness review;
8. non-material revision preserving targeted authority and remaining `VERIFIED`;
9. material Shipment ID revision invalidating targeted authority and returning to `REVIEW_REQUIRED`.

The synthetic harness review is not a customer/reviewer metric.

## Optional signing boundary

Run `33296171708` then reached Processor `/sign`, which returned HTTP 400.

An isolated diagnostic avoided any further Data Extraction use and tested:

`synthetic PDF -> Processor canonicalization -> Processor /sign`

Run `33296422243`:

- Processor normalization: PASS;
- canonical PDF SHA-256: `30a967bcacfa8b84af573d530a8d6d77292579adf87fbd9380aafa4e77d3af83`;
- `/sign`: `FAIL_HTTP_400`;
- artifact `9727544255`;
- artifact ZIP SHA-256 `9e6f0d73e0707d826e300dadbc2b02fbf7527c7a229b73998143493ac7e17058`.

Therefore signing remains an independent provider/account/service limitation. No more signing calls should be made without a specific Nutrient correction or entitlement explanation.

## Semantic truth boundary

ReleaseProof separates three questions:

1. **Integrity:** are exact document/page/provider artifacts untampered? Hashes and provider receipts answer this.
2. **Review identity:** is this still the same business evidence? The deterministic key is logical document, page, field path, normalized value, bbox within historical tolerance, and coordinate space.
3. **Authority semantics:** under which comparison rules may historical human authority continue? The `EvidenceEquivalencePolicy` frozen inside the review answers this.

Confidence remains a review-routing/admissibility signal and is intentionally not semantic identity.

A source revision always mints a new current manifest. Only still-grounded authority can carry forward under the exact policy stored with the historical review.

## Historical chronology

The earlier Processor-only accepted proof remains run `32215337912`, artifact `9352133498`, digest `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`.

Later historical attempts encountered:

- HTTP 402 quota exhaustion;
- v2 run `33295050008`: Processor PASS, Data Extraction HTTP 403 because the Processor credential was mistakenly used for the separate Data Extraction product;
- v2 run `33295993491`: separate credential accepted, Data Extraction HTTP 400 because the acceptance schema contained the unsupported `additionalProperties` keyword.

Those failures are retained as chronology. They are not the current hosted-v2 state.

## Production evidence

The last accepted Vercel deployment predates the new v2 hosted result. Until redeployed, production is **STALE** with respect to the new status fields.

Target production endpoints after redeploy:

- `/`
- `/health`
- `/api/live-evidence` - backward-compatible historical receipt
- `/api/v2-evidence` - current v2 hosted evidence
- `/api/demo`
- `/api/evaluation`

## Compliance and IP boundaries

Frozen policy, deterministic replay and tamper-evident hashes support auditability but do not by themselves establish legal non-repudiation or regulatory compliance/certification.

ReleaseProof does not claim invention of provenance graphs, version-aware approvals, dependency invalidation, ontologies, or knowledge graphs. It does not copy proprietary OntoGuard schemas, algorithms, policy language or implementation details. The independently developed contribution is DWS-grounded semantic review continuity with frozen historical authority and selective invalidation.
