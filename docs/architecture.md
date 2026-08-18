# Architecture

```text
Invoice / shipping document / certificate
                |
                v
Nutrient DWS Processor /build                 LIVE GATE
json-content + keyValuePairs                  (no fixture fallback)
                |
      page + bbox + confidence + value
                v
Fail-closed Evidence Normalizer
                |
                v
Deterministic Reconciliation
   MATCH / LOW_CONFIDENCE / MISMATCH / MISSING
                |
                v
Human Review Surface
review binds exact finding/evidence slice
                |
                v
Current Release Manifest
whole-document digests + DWS receipt digests + findings + reviews
                |
      source revision -> reprocess current packet
                v
Differential Reverification
 preserve review only if current finding binding is identical
                |
       +--------+---------+
       |                  |
    VERIFIED       REVIEW_REQUIRED / BLOCKED
```

## Important distinction

Any document-byte change makes the historical manifest non-current. Differential Reverification does **not** revive the old manifest. It creates a new manifest after current extraction/reconciliation and may carry forward only a human review whose material finding binding is reproduced exactly.

## Security boundary

`NUTRIENT_API_KEY` is server-side only. Live DWS calls fail closed if credentials are absent, the HTTP call fails, the response is not JSON, or expected source grounding is missing. Controlled fixtures are visibly labeled and never promoted to live evidence.


Render-ready Mermaid source: [`architecture.mmd`](architecture.mmd).
