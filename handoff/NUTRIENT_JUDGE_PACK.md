# Nutrient DWS Challenge - Submission Handoff

## Identity

**Canonical project name:** ReleaseProof

**One-line pitch:** When a document packet changes, ReleaseProof reprocesses current source-grounded evidence and preserves human authority only if the same logical finding still reproduces from semantically equivalent evidence under the exact policy frozen when that authority was granted.

**Invention:** Differential Reverification with evidence-scoped human authority, frozen equivalence policy and reminted current release state.

**Submission status:** **READY** except final media/form work and a production redeploy of the updated evidence surface.

## Prize thesis

The memorable mechanism is not “AI reads PDFs.” Nutrient already provides document processing and grounding.

ReleaseProof answers a different question:

> After evidence changes, which historical human decisions are still valid, under the exact rules that were in force when those decisions were granted?

The mechanism separates:

1. cryptographic integrity;
2. semantic evidence identity;
3. historical human authority semantics.

**Memory hook:** “The human decision carries its own rules of continued validity.”

## Product boundary

Nutrient owns:

- Processor OCR/flatten/page operations;
- Data Extraction grounding;
- Viewer annotations/comments/layers;
- digital-signature tooling.

ReleaseProof owns:

- cross-document reconciliation;
- stable logical finding identity;
- human authority binding;
- frozen historical equivalence policy;
- Differential Reverification;
- selective invalidation/carry-forward;
- current release lifecycle.

Semantic review key:

`logical document + page + field path + normalized value + bbox within tolerance + coordinate space`

Confidence routes review but is not semantic identity.

## Frozen authority against silent policy drift

Every new semantic `HumanReview` stores `EvidenceEquivalencePolicy` with:

- version `evidence-equivalence/1`;
- bbox tolerance;
- normalization version `nfkc-whitespace/1`;
- bbox metric `axis-absolute/1`.

`authority_binding` commits to the finding, reviewer decision, reviewer identity, rationale, reviewed evidence identities and frozen policy.

A later runtime default cannot rescue or invalidate an old review by silently changing tolerance. Unknown historical policy versions fail closed. Legacy reviews with no policy remain exact-binding only.

This is auditability/deterministic replay, not a claim of SOC 2, FDA 21 CFR Part 11, ISO compliance/certification or legal non-repudiation.

## Hosted DWS-native v2 core - PASS

Accepted current hosted run:

- workflow run: `33296171708`;
- job: `99216095769`;
- trigger commit: `0a0e3d1d9a38f2ebfe5a50712222741d4930f018`;
- artifact: `9727472871`;
- artifact ZIP SHA-256: `fc7b7b9cfc2cee71912e59580f53ada8f03098b8532266f0cbf6507021f3bab2`.

Provider calls:

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

### What the live run proved

Before the optional signing call was reachable, the harness had already asserted:

- Processor OCR + flatten canonicalization: **PASS_HOSTED**;
- Data Extraction on canonical renditions: **PASS_HOSTED**;
- grounded page/bbox/confidence/source evidence: **PASS_HOSTED**;
- native canonical page isolation: **PASS_HOSTED**;
- canonical page SHA-256 binding: **PASS_HOSTED**;
- coordinate space `nutrient-processor-canonical-rendition/1`: **PASS_HOSTED**;
- intentional cross-document Shipment ID mismatch: **PASS_HOSTED**;
- synthetic acceptance-harness review brought baseline to `VERIFIED`: **PASS**;
- byte-different non-material revision preserved targeted historical authority and remained `VERIFIED`: **PASS_HOSTED**;
- material Shipment ID revision invalidated targeted authority and returned to `REVIEW_REQUIRED`: **PASS_HOSTED**.

Therefore **DWS-native Differential Reverification core = PASS_HOSTED**.

The review used in this acceptance is explicitly synthetic. It is not a real customer approval or reviewer-time metric.

## Optional signing - FAIL_HTTP_400

The same live run reached Processor `/sign` only after all core assertions above had passed. `/sign` returned HTTP 400.

A separate low-cost diagnostic tested a Processor-normalized synthetic PDF without any Data Extraction calls:

- run: `33296422243`;
- job: `99216757835`;
- artifact: `9727544255`;
- artifact ZIP SHA-256: `9e6f0d73e0707d826e300dadbc2b02fbf7527c7a229b73998143493ac7e17058`;
- Processor normalization: **PASS**;
- `/sign`: **FAIL_HTTP_400**.

This rules out the narrow explanation that only the locally generated pre-normalized PDF caused the failure. Signing remains a separate provider/account/service limitation and is not required for the core invention claim.

Do not make more signing calls unless Nutrient gives a specific entitlement/configuration or request-shape correction.

## Viewer boundary

The Viewer projection is covered by deterministic tests for:

- finding annotation;
- reviewer-specific layer;
- review comment metadata;
- named approved-state layer.

Hosted Viewer execution remains **UNRUN**. Do not call it PASS.

## Historical hosted proof

Historical Processor-only acceptance remains immutable evidence:

- run `32215337912`;
- commit `d885ed31ebb8cc9449c450b0334c630c3b11f656`;
- artifact `9352133498`;
- digest `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`;
- manifest `a5716cc3f5580a6dde1e21d4199675bb65f2b46e92b7b65a334f05a1d57663cc`.

That run produced a real cross-document Shipment ID disagreement and ReleaseProof returned `REVIEW_REQUIRED` instead of silently releasing.

Its response omitted documented `pageIndex`. Nutrient Solutions Engineering confirmed this was a real provider/documentation discrepancy and escalated it. ReleaseProof's historical compatibility path uses ordered page position only when `pageIndex` is absent and fails closed when a present index is malformed.

## Failure chronology retained honestly

Do not hide the development evidence:

- earlier hosted Differential Reverification attempt: HTTP 402 after quota exhaustion;
- run `33295050008`: Processor canonicalization PASS, Data Extraction HTTP 403 because the historical Processor key was used instead of the separate Data Extraction product key;
- run `33295993491`: credential class corrected, Data Extraction HTTP 400 due unsupported `additionalProperties` in acceptance schema;
- run `33296171708`: DWS-native core reached and passed all Differential Reverification assertions; optional signing then returned HTTP 400.

The first three states are chronology, not the current core acceptance state.

## Public judge surface

Production URL:

`https://evidencebound-releaseproof-dws.vercel.app`

Repository:

`https://github.com/evidencebound/evidencebound-releaseproof-dws`

The last accepted Vercel deployment predates the new hosted-v2 evidence. Production is therefore **STALE** until redeployed from current `main`.

Target judge endpoints after redeploy:

- `/` - current judge narrative;
- `/health` - `dws_native_v2_core_hosted=PASS`, signing `FAIL_HTTP_400`, Viewer `UNRUN`;
- `/api/live-evidence` - backward-compatible historical Processor receipt;
- `/api/v2-evidence` - current v2 hosted evidence;
- `/api/demo`;
- `/api/evaluation`.

No public route performs live Nutrient calls.

## Prize narrative

**Progress:** public implementation, real historical Processor evidence, current hosted Processor + Data Extraction + canonical-page evidence, hosted Differential Reverification, frozen historical authority semantics, public CI on Python 3.11/3.12/3.13, production evidence surface pending current redeploy.

**Concept:** byte changes should not blindly reset all human work, and stable filenames should not blindly preserve it. ReleaseProof proves whether reviewed business evidence is still equivalent and evaluates historical authority under its original comparison policy.

**Feasibility:** Nutrient does native document work; ReleaseProof stays focused on reconciliation, authority continuity and selective invalidation. The competition-critical v2 core now has hosted evidence rather than contract-only evidence.

**Sponsor memory hook:** “After the packet changes, prove which human review is still grounded in current evidence under the rules the reviewer actually approved, and which one is not.”

## Current limitations

- Processor `/sign`: **FAIL_HTTP_400**;
- hosted Viewer flow: **UNRUN**;
- Nutrient Studio schema generation: **UNRUN / not claimed**;
- real reviewer-time/customer metrics: **UNVERIFIED**;
- regulatory compliance/certification: **NOT CLAIMED**.

## Capture targets

Prioritize in final media/application:

1. `DWS-NATIVE V2 CORE - HOSTED PASS` evidence and run id `33296171708`;
2. canonical Processor rendition -> Data Extraction grounding -> page hash;
3. non-material revision -> authority preserved -> `VERIFIED`;
4. material Shipment ID change -> authority invalidated -> `REVIEW_REQUIRED`;
5. Frozen Authority Policy example: review at tolerance 2.0 cannot be reinterpreted by later runtime 10.0;
6. explicit limitation: optional signing HTTP 400, Viewer UNRUN;
7. boundary: Nutrient produces trustworthy document evidence; ReleaseProof determines whether historical human authority still holds.

See `README.md`, `docs/hosted-v2-core-acceptance-2026-08-30.md`, `docs/live-dws-evidence.md`, `docs/frozen-authority-policy.md`, `docs/claims-ledger.md`, and `qa/QA_RECEIPT.json`.
