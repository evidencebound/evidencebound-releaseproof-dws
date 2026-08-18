# Commercial Thesis

## ICP

Trade-compliance teams, customs brokers, freight forwarders, import/export operations and enterprise procurement teams that reconcile document bundles before consequential release or filing.

## Economic problem

When a packet is amended, teams either risk reusing a stale exception or repeat human review broadly. The commercial hypothesis is that source-grounded Differential Reverification can narrow repeated review to the material evidence that actually changed while retaining a replayable release record.

## Paid differentiation

- Nutrient DWS as deterministic document-processing boundary;
- claim-level source grounding with page/bounds/confidence;
- deterministic cross-document reconciliation;
- evidence-scoped human reviews;
- new release manifest for every current packet;
- selective review preservation only when the current evidence binding reproduces;
- fail-closed stale/material-change handling;
- audit/replay API suitable for ERP/TMS/customs integration.

## Free/incumbent alternatives

Manual comparison, generic OCR + spreadsheet review, document-management approval history, and provenance/signature systems. ReleaseProof must earn its place by reducing avoidable re-review without expanding trust beyond current evidence.

## Pricing hypothesis

B2B usage pricing per packet plus audit-retention/integration tier. No willingness-to-pay study has been run; pricing is a hypothesis, not evidence.

## Pilot design

Choose one high-volume packet type with 3–5 material fields across invoice, transport and certificate. Measure:
- exception/revision frequency;
- percentage of revisions where reviewed evidence is unchanged;
- reviewer minutes per revision;
- false preservation rate (kill criterion: must remain zero under labelled test set);
- replay success and integration effort.
