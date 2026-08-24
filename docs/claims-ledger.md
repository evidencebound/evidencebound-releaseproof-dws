# Claims Ledger

| Claim | Evidence class | Status |
|---|---|---|
| controlled packet reaches `REVIEW_REQUIRED` then `VERIFIED` after scoped review | deterministic fixtures/tests | VERIFIED / public CI |
| non-material whole-file revision creates a new manifest and preserves the unchanged review | controlled evaluation + parity-locked retained result | VERIFIED / public CI |
| confidence-only drift does not by itself change semantic evidence identity | semantic reverification regression test | VERIFIED / public CI |
| normalized-value change invalidates prior review authority | controlled evaluation + regression test | VERIFIED / public CI |
| bbox movement within the review's frozen tolerance can preserve review; movement outside it invalidates review | semantic reverification regression tests | VERIFIED / public CI |
| later runtime bbox defaults cannot reinterpret an existing policy-bound review | frozen-policy regression test | VERIFIED / public CI |
| unsupported equivalence-policy versions fail closed to `REVIEW_REQUIRED` | frozen-policy regression test | VERIFIED / public CI |
| changing the frozen equivalence policy changes `authority_binding` | authority-binding regression test | VERIFIED / public CI |
| negative bbox tolerances are rejected | policy validation test | VERIFIED / public CI |
| legacy reviews without frozen policy are not assigned inferred tolerance and remain exact-binding only | engine implementation + compatibility semantics | VERIFIED / public CI |
| page-7 integrity change can leave page-2 review authority valid | page-level blast-radius regression test | VERIFIED / public CI |
| stable logical finding ID is separate from changing semantic evidence binding | semantic reverification regression test | VERIFIED / public CI |
| malformed/missing source grounding fails closed | normalizer tests | VERIFIED / public CI |
| controlled fixtures are explicitly distinguishable from live DWS | provenance labels/UI/tests | VERIFIED / public CI |
| retained `results/controlled-demo.json` and `results/evaluation.json` match current executable mechanism | retained-result parity tests | VERIFIED / public CI at run `32750626503`; final PR-head rerun required after later docs/UI changes |
| hosted DWS request reached real Processor `/build` using repository secret | historical live GitHub Actions | VERIFIED |
| hosted Processor returned parseable grounded key/value content with bbox and confidence | historical hosted Actions + retained artifact | VERIFIED |
| live response may omit documented `pageIndex`; ordered-page-position compatibility is provenance-labelled and malformed present indices fail closed | live diagnostic + public CI | VERIFIED |
| real hosted DWS processed a three-document synthetic packet and produced a current manifest | run `32215337912` | VERIFIED |
| live ReleaseProof detected a cross-document disagreement and returned `REVIEW_REQUIRED` rather than releasing | historical live manifest | VERIFIED |
| Processor-native OCR + flatten canonicalization adapter is implemented | contract tests | VERIFIED / hosted UNRUN |
| Processor-native page isolation uses `parts[].pages` rather than local splitting | contract tests | VERIFIED / hosted UNRUN |
| Data Extraction adapter uses `/extraction/extract` with external schema and `citationsEnabled: true` | contract tests against official request shape | VERIFIED / hosted UNRUN |
| Data Extraction normalizer consumes provider page/bbox/confidence/source evidence and fails closed if grounding is missing | contract tests | VERIFIED / hosted UNRUN |
| production schema is generated/refined in Nutrient Studio | provider execution | UNVERIFIED; repository only accepts external schema and makes no Studio-generation claim |
| Viewer finding/review maps to annotation + reviewer-specific layer/comment + named approved layer | deterministic projection contract | VERIFIED / hosted Viewer UNRUN |
| release artifact can be sealed through Processor `/sign` adapter | contract test | VERIFIED / hosted signing UNRUN |
| hosted Differential Reverification preserves review after non-material revision | live differential acceptance | NON-BLOCKING LIMITATION - QUOTA_402 |
| public repository and Python 3.11/3.12/3.13 GitHub Actions matrix | GitHub repository / Actions | 56/56 PASS per lane at run `32750626503`; final PR-head rerun required after later docs/UI changes |
| public Vercel evidence URL serves health/live-evidence/evaluation/demo paths | previous production acceptance | VERIFIED HISTORICALLY; refactor deployment requires new acceptance |
| public Vercel service performs no runtime Nutrient calls | route surface + source + health contract | VERIFIED HISTORICALLY; recheck after deploy |
| Differential Reverification addresses a real corrected/re-issued packet workflow | Nutrient Solutions Engineering field feedback from customer projects | EXTERNAL FIELD OBSERVATION, not a market-size or roadmap claim |
| mechanism reduces real reviewer time | field study | UNVERIFIED |
| frozen-policy mechanism establishes SOC 2/FDA/ISO compliance or legal non-repudiation | broader operational/regulatory assessment | NOT CLAIMED |

## Semantic v3 truth boundary

ReleaseProof separates three questions:

1. **Integrity:** are these exact document/page/provider artifacts untampered? Cryptographic hashes and provider receipts answer this.
2. **Review identity:** is this still the same business evidence a human reviewed? A deterministic semantic key answers this: logical document, page, field path, normalized value, and bounding box within an explicit tolerance.
3. **Authority semantics:** under which comparison rules was the human decision allowed to continue after evidence changed? The `EvidenceEquivalencePolicy` frozen inside the review answers this.

Confidence remains a review-routing/admissibility signal and is intentionally not part of semantic evidence identity.

The old manifest never becomes current after a source revision. Differential Reverification always mints a new current manifest and carries forward only still-grounded human authority evaluated under the policy stored in that historical review.

## Frozen policy and AuthorityBinding

New semantic reviews store:

- policy version `evidence-equivalence/1`;
- bbox tolerance;
- normalization version `nfkc-whitespace/1`;
- bbox metric `axis-absolute/1`.

`authority_binding` commits to the finding, exact finding binding, reviewer decision, reviewer identity, rationale, evidence identities, and frozen equivalence policy.

A later runtime cannot change the meaning of an old review by changing its bbox default. Unsupported policy versions fail closed. Legacy reviews without policy remain exact-binding only; ReleaseProof does not infer a historical tolerance that was never recorded.

See `docs/frozen-authority-policy.md`.

## Canonical hosted evidence

The competition-critical hosted proof remains GitHub Actions run `32215337912` at commit `d885ed31ebb8cc9449c450b0334c630c3b11f656`, artifact `9352133498`, digest `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`.

That run used the historical Processor `json-content` path. It is not relabelled as Data Extraction API acceptance.

The later quota-aware Differential Reverification harness passed public CI (`32215419913`) but hosted run `32215515505` received HTTP `402` on the first `/build`. Further calls were stopped. This remains a non-blocking quota limitation, not converted into PASS or mechanism failure.

## DWS-native hosted status

The following paths are implemented and contract-tested but remain **UNRUN** with hosted credentials:

- Processor OCR/flatten canonicalization;
- Processor page isolation for canonical page hashes;
- Data Extraction `/extraction/extract`;
- DWS Viewer review flow;
- Processor `/sign`.

No hosted PASS is claimed for these paths until a real acceptance run succeeds.

## Public production evidence

Previously accepted Vercel project: `evidencebound-releaseproof-dws` (`prj_zYwz9jdjY3PmbpoYFWUraPkLUPET`). Historical production deployment: `dpl_DgptupzTPrqx9HsySqWtwenmUNoA`.

After this refactor merges, production acceptance must be rerun before the refactored code is classified as production PASS.

## Compliance claim boundary

Frozen policy, deterministic replay and tamper-evident hashes are useful controls for auditability. They do not by themselves establish legal non-repudiation or compliance/certification under SOC 2, FDA 21 CFR Part 11, ISO or another regulatory framework. Identity assurance, qualified signatures where required, access controls, retention, validation, operational controls and independent audits remain outside this mechanism.

## IP / prior-art boundary

ReleaseProof does not claim invention of provenance graphs, version-aware approvals, dependency invalidation, ontologies, or knowledge graphs. It does not copy OntoGuard ontology schemas, proprietary algorithms, policy language, implementation details, or product claims.

The independently developed ReleaseProof contribution is the DWS-grounded semantic review-continuity and selective invalidation mechanism. EvidenceBound Core transfer candidates are limited to generic typed evidence identity, frozen authority policy/binding, explicit dependency edges, deterministic equivalence, and blast-radius semantics.
