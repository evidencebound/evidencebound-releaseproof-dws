# DevNetwork + Nutrient Judge Mapping

## Progress

Implemented now:
- DWS Processor transport and strict response normalizer;
- trade-packet reconciliation;
- source-grounded findings;
- scoped human review;
- current release manifests;
- Differential Reverification;
- controlled evaluation and premium local judge UI;
- 20 tests, packaging and compile gates;
- fail-closed no-key live probe.

Gap: real DWS call and public deployment remain external blockers. The public repository now exists; GitHub CI becomes evidence only after the published source head completes successfully. Final video remains a separate submission-handoff item.

## Concept

Real problem: document revisions create a choice between stale approval reuse and blanket re-review. ReleaseProof remanifests every current packet while preserving only human review whose material finding binding is exactly reproduced.

## Feasibility

Commercial wedge: trade/compliance packet reconciliation; API-first integration with ERP/TMS/customs workflow. Pricing and customer demand remain hypotheses pending pilot discovery.

## Nutrient sponsor fit

- DWS performs core `/build` document extraction, not a throwaway call.
- source grounding uses page/bbox/confidence.
- uncertain/mismatched findings route to human review.
- current state and historical manifest are separately represented.
- changed material evidence invalidates scoped review.
- live DWS proof remains mandatory before submission claims integration PASS.
