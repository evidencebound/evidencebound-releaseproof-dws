# Claims Ledger

| Claim | Evidence class | Status |
|---|---|---|
| controlled packet reaches REVIEW_REQUIRED then VERIFIED after scoped review | deterministic fixtures/tests | VERIFIED locally |
| non-material file revision creates a new manifest and preserves 1/1 unchanged scoped review in retained fixture | controlled evaluation | VERIFIED locally |
| reviewed evidence-slice change invalidates 1/1 prior scoped review in retained fixture | controlled evaluation | VERIFIED locally |
| malformed/missing source grounding fails closed | tests | VERIFIED locally |
| controlled fixtures are explicitly distinguishable from live DWS | provenance labels/UI/tests | VERIFIED locally |
| missing `NUTRIENT_API_KEY` produces fail-closed live probe | local negative test | VERIFIED locally |
| hosted DWS request matches implemented Processor `/build` contract | source + contract tests against documented shape | VERIFIED at contract level |
| real competition DWS account returns compatible extraction for three packet PDFs | live API execution | UNVERIFIED / BLOCKED |
| DWS Viewer human-review integration | live/product implementation | UNRUN |
| public judge URL/CI | external deployment/repo | UNVERIFIED / BLOCKED |
| mechanism reduces real reviewer time | field study | UNVERIFIED |
