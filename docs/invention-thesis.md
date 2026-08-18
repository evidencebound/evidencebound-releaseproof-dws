# Invention Thesis — Differential Reverification

## Problem

Document approval systems can record that a version was reviewed. Provenance systems can record where data came from. Neither fact alone minimizes repeated human work after a packet changes: a whole-file revision can force blanket re-review even when the source-grounded evidence for a previously reviewed exception is unchanged.

## Mechanism

ReleaseProof creates **evidence-scoped review bindings** from DWS-grounded claim slices. A review binds to the exact normalized evidence slice used by a finding: logical document identity, normalized field, label, value, page, bounds, and confidence. The released packet still binds whole-document hashes and the complete manifest; a changed document therefore never makes the old manifest current.

On revision, **Differential Reverification**:

1. reprocesses the current documents through the document extraction boundary;
2. recomputes findings from current evidence;
3. compares each prior review binding to the currently reproduced finding binding;
4. preserves only reviews whose evidence slice is unchanged;
5. invalidates reviews whose material evidence changed or disappeared;
6. mints a new current manifest and release state.

This makes the trust primitive selective: change triggers recomputation, but does not automatically destroy human work that is still grounded in identical material evidence.

## Falsifiable claims

- a non-material document revision that leaves the reviewed evidence slice unchanged produces a new manifest while preserving the scoped review;
- a material revision of the reviewed evidence produces a new finding/review requirement and cannot reuse the old approval;
- tampering with the historical manifest blocks verification;
- missing grounding metadata fails closed.

## Novelty boundary

Version-aware approvals and provenance dependency invalidation predate this project. The candidate contribution is the combination of DWS source-grounded extraction, evidence-scoped human review tokens, selective review preservation, and a new release manifest for each current packet. We do **not** claim this pattern is patent-novel or historically first.
