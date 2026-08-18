# Prior-Art Gate — ReleaseProof

## Directly overlapping prior art

- W3C PROV provides a general model for provenance entities, activities, and agents.
- C2PA Content Credentials binds signed provenance/assertions to digital assets.
- Electronic-document workflow patents already describe approvals of current document versions and signatures over material data.
- Earlier provenance/version-control patents describe computing descendants of changed state in a provenance DAG and invalidating dependent state.

These sources eliminate any strong claim that ReleaseProof invented version-aware approval, provenance graphs, or downstream invalidation.

## Remaining competition thesis

Nutrient exposes source-grounded extraction with page/bounds/confidence and supports deterministic document operations. ReleaseProof uses those signals to make review *differential*: a current packet is always remanifested after source changes, but a human exception can be reused only when its exact normalized DWS evidence slice is reproduced. This is designed to reduce blanket re-review while failing closed on material changes.

## Novelty confidence

**Moderate-low as a broad invention claim; moderate as a concrete product/control primitive.** The strongest case is not “nobody has versioned approvals.” It is the implemented selective evidence-scoped reverification behavior, sponsor-authentic DWS integration, and a high-value trade-document workflow.

## Kill criterion

If live DWS output cannot provide stable enough source grounding to distinguish material from non-material revisions safely, Differential Reverification should be killed or narrowed rather than simulated with fixture-only metadata.
