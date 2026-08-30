# Hosted DWS-native v2 Core Acceptance - 2026-08-30

## Decision

**DWS-native v2 core: PASS_HOSTED.**

**Optional Processor digital signing: FAIL_HTTP_400.**

**Hosted Viewer review execution: UNRUN.**

The core PASS does not include signing. It is supported by deterministic control flow in the accepted live harness: the signing call is reachable only after all Processor canonicalization, Data Extraction, canonical page-grounding and Differential Reverification assertions have passed.

## Accepted core run

- GitHub Actions workflow: `live-dws-v2`
- run id: `33296171708`
- hosted job id: `99216095769`
- trigger commit: `0a0e3d1d9a38f2ebfe5a50712222741d4930f018`
- artifact id: `9727472871`
- artifact ZIP SHA-256: `fc7b7b9cfc2cee71912e59580f53ada8f03098b8532266f0cbf6507021f3bab2`

Only synthetic documents were sent to Nutrient. Credentials and raw provider payloads are not retained in the public evidence artifact.

## Provider-call ledger

```json
{
  "processor": {
    "canonicalize": 5,
    "isolate_page": 5,
    "sign": 1
  },
  "data_extraction": 5
}
```

## Core gates proved by execution order

Before `sign_pdf()` can be called, the harness requires all of the following to succeed:

1. Three baseline synthetic PDFs are canonicalized by Processor.
2. Data Extraction succeeds on each canonical rendition.
3. Each normalized document contains grounded fields.
4. Each retained field has a canonical page SHA-256.
5. Each retained bbox is explicitly in coordinate space `nutrient-processor-canonical-rendition/1`.
6. Source evidence and normalized confidence are present and valid.
7. The intentional cross-document Shipment ID mismatch is reproduced.
8. Clearly labelled synthetic acceptance-harness reviews bring the baseline packet to `VERIFIED`.
9. A byte-different but semantically non-material invoice revision is re-canonicalized and re-extracted.
10. The targeted prior review is present in `preserved_review_ids` and the new packet remains `VERIFIED`.
11. A material Shipment ID revision is re-canonicalized and re-extracted.
12. The targeted prior review is present in `invalidated_review_ids` and the new packet returns to `REVIEW_REQUIRED`.
13. Only after those assertions does the harness attempt Processor `/sign`.

Run `33296171708` failed at step 13 with `DWS signing returned HTTP 400`. Therefore steps 1-12 are accepted hosted evidence; signing is not.

## Data Extraction evidence

The successful hosted responses exposed the grounded structures ReleaseProof needs, including schema-shaped `output.data`, field metadata containing bbox, confidence, `pageIndex`, page number and source bbox identifiers, plus page dimensions. ReleaseProof normalized those fields and then used native Processor page isolation to produce canonical page hashes.

The acceptance used separate product credentials:

- Processor: `NUTRIENT_API_KEY`
- Data Extraction: `NUTRIENT_DATA_EXTRACTION_API_KEY`

Both are preflighted before network execution.

## Differential Reverification result

The live hosted path exercised both sides of the invention thesis:

- **non-material revision:** source bytes changed, semantic evidence remained equivalent under the frozen review policy, targeted historical authority was preserved, and the new packet remained `VERIFIED`;
- **material revision:** reviewed Shipment ID evidence changed, targeted historical authority was invalidated, and the new packet returned to `REVIEW_REQUIRED`.

The harness review is synthetic and exists only to test authority continuity. It is not a real reviewer-time, customer-approval or adoption metric.

## Optional signing diagnostic

To avoid repeating Data Extraction calls, signing was tested independently with a Processor-normalized synthetic PDF.

- workflow run: `33296422243`
- job id: `99216757835`
- trigger commit: `81dc19b39af3cc75f3c1b6e360e85c26dfdb290f`
- artifact id: `9727544255`
- artifact ZIP SHA-256: `9e6f0d73e0707d826e300dadbc2b02fbf7527c7a229b73998143493ac7e17058`
- Processor normalization: **PASS**
- canonical PDF SHA-256: `30a967bcacfa8b84af573d530a8d6d77292579adf87fbd9380aafa4e77d3af83`
- `/sign`: **FAIL_HTTP_400**

This disproves the narrow hypothesis that the signing failure was caused only by sending the locally generated pre-normalized PDF. No further signing calls should be made without a specific Nutrient entitlement/configuration correction or request-shape clarification.

## Viewer boundary

`releaseproof.viewer` remains contract-tested as a projection to annotation/comment/layer concepts. A real hosted Viewer review session has not been executed and remains **UNRUN**.

## Claim boundary

What may be claimed:

- hosted Processor canonicalization: PASS;
- hosted Data Extraction grounding: PASS;
- hosted canonical page isolation/hash path: PASS;
- hosted DWS-native Differential Reverification core: PASS;
- non-material authority preservation: PASS;
- material authority invalidation: PASS;
- optional signing: FAIL_HTTP_400;
- hosted Viewer flow: UNRUN.

What may not be claimed:

- full end-to-end signed release PASS;
- hosted Viewer PASS;
- real reviewer-time savings;
- customer adoption;
- regulatory certification or legal non-repudiation.
