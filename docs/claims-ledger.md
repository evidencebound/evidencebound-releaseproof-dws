# Claims Ledger

| Claim | Evidence class | Status |
|---|---|---|
| controlled packet reaches REVIEW_REQUIRED then VERIFIED after scoped review | deterministic fixtures/tests | VERIFIED locally + public CI |
| non-material file revision creates a new manifest and preserves 1/1 unchanged scoped review in retained fixture | controlled evaluation | VERIFIED locally + public CI |
| reviewed evidence-slice change invalidates 1/1 prior scoped review in retained fixture | controlled evaluation | VERIFIED locally + public CI |
| malformed/missing source grounding fails closed | tests | VERIFIED locally + public CI |
| controlled fixtures are explicitly distinguishable from live DWS | provenance labels/UI/tests | VERIFIED locally + public CI |
| missing `NUTRIENT_API_KEY` produces fail-closed live probe | local negative test | VERIFIED locally |
| hosted DWS request reaches real Processor `/build` using repository secret | live GitHub Actions | VERIFIED |
| hosted DWS returns parseable `json-content` with grounded key/value content, bbox and confidence | hosted GitHub Actions + retained artifact | VERIFIED |
| live response may omit documented `pageIndex`; ordered-page-position compatibility is provenance-labelled and malformed present indices still fail closed | live diagnostic + 27-test public CI | VERIFIED |
| real hosted DWS processes a three-document synthetic packet through the post-drift normalizer and emits a current manifest | run `32215337912` | VERIFIED |
| every retained live field has page provenance, bbox, normalized confidence and evidence-slice digest | live workflow verification + artifact | VERIFIED |
| live ReleaseProof detects a cross-document disagreement produced by hosted extraction and returns REVIEW_REQUIRED rather than releasing | live manifest | VERIFIED |
| hosted Differential Reverification preserves an unchanged review after a non-material revision | live differential acceptance | BLOCKED_QUOTA_402 |
| deterministic Differential Reverification preserves 1/1 unchanged scoped review and invalidates it after evidence-slice change | controlled evaluation | VERIFIED |
| public repository and GitHub Actions test matrix | GitHub repository / Actions | VERIFIED |
| DWS Viewer human-review integration | live/product implementation | UNRUN |
| public judge URL | external deployment | UNVERIFIED / BLOCKED |
| mechanism reduces real reviewer time | field study | UNVERIFIED |

## Canonical hosted evidence

Core DWS evidence is anchored to GitHub Actions run `32215337912` at commit `d885ed31ebb8cc9449c450b0334c630c3b11f656`, artifact `9352133498`, digest `sha256:485f9d1a72f4b4129944994949439ca3d14ff53202f6ab4ff7e20b88b5f6964e`.

The later quota-aware Differential Reverification harness passed public CI (`32215419913`) but its hosted rerun `32215515505` received HTTP `402` on the first `/build`. Further live calls were stopped. This is recorded as a quota blocker, not converted into a mechanism failure or success.

Sanitized acceptance receipts are retained in GitHub issue #3. API credentials and extracted document text are excluded.
