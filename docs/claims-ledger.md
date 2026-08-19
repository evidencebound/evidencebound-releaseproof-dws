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
| hosted DWS returns parseable `json-content` with grounded `keyValuePairs` for synthetic PDF | live schema-only GitHub Actions diagnostic | VERIFIED |
| live response may omit documented `pageIndex`; ordered-page-position compatibility is provenance-labelled and malformed present indices still fail closed | live diagnostic + regression tests | VERIFIED at compatibility-mechanism level |
| public repository and GitHub Actions test matrix | GitHub repository / Actions | VERIFIED |
| real DWS account processes all three packet PDFs through the post-drift normalizer and emits a current manifest | live API execution | FAIL pending post-fix rerun |
| DWS Viewer human-review integration | live/product implementation | UNRUN |
| public judge URL | external deployment | UNVERIFIED / BLOCKED |
| mechanism reduces real reviewer time | field study | UNVERIFIED |

## Live evidence receipts

Sanitized live acceptance receipts are retained in GitHub issue #3. They contain run/commit identity and step outcomes only; API credentials and extracted document text are excluded.
