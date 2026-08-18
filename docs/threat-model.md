# Threat Model

## Protected claims

ReleaseProof protects the narrow claim that a release decision is bound to the exact document bytes, DWS extraction receipts, deterministic findings, scoped human decisions, and policy version represented by the manifest.

## Threats handled

- source document changed after review → `INVALIDATED`;
- manifest payload tampering → `BLOCKED`;
- missing required field → `BLOCKED`;
- low extraction confidence → `REVIEW_REQUIRED`;
- cross-document mismatch → `REVIEW_REQUIRED`;
- a review replayed against a changed finding → ignored unless its finding binding still matches;
- missing source grounding in the spatial adapter → fail closed.

## Explicit non-goals

- proving a source document is truthful;
- verifying legal or regulatory compliance;
- authenticating reviewer identity in v0.1;
- proving DWS itself was uncompromised;
- immutable storage;
- qualified electronic signatures;
- replacing customs, legal, or compliance professionals.

## Secret boundary

`NUTRIENT_API_KEY` is server-only. It is not accepted from browser query parameters, committed fixtures, or public configuration.
