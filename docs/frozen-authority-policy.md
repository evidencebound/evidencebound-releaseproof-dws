# Frozen Human Authority Policy

## Problem

A historical human approval must not be reinterpreted under whatever semantic comparison defaults happen to exist in a later runtime.

Without a frozen policy, this sequence is unsafe:

```text
T0 reviewer approves finding with bbox tolerance = 2.0
T1 code default changes to bbox tolerance = 5.0
T2 old approval is replayed under the new rule
```

That is silent policy drift. It can either preserve authority that the reviewer never granted or invalidate authority under rules that did not exist when the reviewer made the decision.

## ReleaseProof rule

Every new semantic `HumanReview` stores the exact `EvidenceEquivalencePolicy` that governed review continuity when authority was created.

Current policy fields:

```text
version             evidence-equivalence/1
bbox_tolerance      2.0
value_normalization nfkc-whitespace/1
bbox_metric         axis-absolute/1
```

The review also exposes an immutable `authority_binding` digest over:

- finding identity and exact finding binding;
- reviewer decision;
- reviewer identity;
- rationale;
- reviewed semantic evidence identities;
- the frozen equivalence policy.

Changing any of those inputs changes the authority binding.

## Reverification semantics

For a policy-bound review, Differential Reverification evaluates current evidence using the policy stored in that review.

Conceptually:

```text
review = H(F, E_old, P_review, decision)
current finding = F(E_new)

preserve authority only if:
  policy P_review is supported
  AND evidence normalization version matches P_review
  AND Equivalent_P_review(E_old, E_new)
```

The runtime's current bbox default cannot loosen or tighten an existing review.

A compatibility `bbox_tolerance` argument remains temporarily in the v2 public function signatures, but it cannot reinterpret policy-bound historical authority.

## Fail-closed migration

Policy evolution is explicit and versioned.

If ReleaseProof encounters a review with an unsupported equivalence-policy version, normalization version, or bbox metric, it does not guess a migration. That review is not accepted as current authority and the finding remains `REVIEW_REQUIRED`.

Legacy reviews created before frozen policy support are also not assigned an inferred tolerance. They remain fail-closed to their exact historical finding binding.

This gives the engine a deterministic migration rule:

```text
known historical policy -> replay under that exact policy
unknown policy -> REVIEW_REQUIRED
legacy exact binding -> exact-match only
```

## DWS boundary

Nutrient DWS owns document evidence primitives such as canonical processing, extraction grounding, Viewer review surfaces and signing paths.

ReleaseProof owns continuity of human authority over that evidence.

```text
Nutrient DWS extraction
        |
        v
source-grounded evidence
        |
        v
human review
        + frozen EvidenceEquivalencePolicy
        |
        v
AuthorityBinding
        |
        v
Differential Reverification
        |
        + preserve only under historical policy
        + otherwise REVIEW_REQUIRED
```

## Verification

Public CI run `32750626503` verifies this kernel on Python 3.11, 3.12 and 3.13.

Relevant regression properties:

- a review created with bbox tolerance `2.0` cannot be preserved by later passing runtime tolerance `10.0` when the evidence moved by `4.0`;
- unknown equivalence-policy versions fail closed;
- changing the frozen policy changes `authority_binding`;
- negative bbox tolerances are rejected;
- existing near/far bbox and page-local blast-radius behavior remains intact.

Full test suite at that code head: **56/56 PASS per Python lane**.

## Auditability claim boundary

This design supports deterministic historical replay, explicit policy provenance, tamper-evident manifest hashing and fail-closed policy evolution.

It does **not**, by itself, establish legal non-repudiation, SOC 2 compliance, FDA 21 CFR Part 11 compliance, ISO certification, or any other regulatory certification. Those outcomes depend on broader identity, signature, access-control, retention, operational and audit controls outside this mechanism.

## Pitch wording

Safe architecture statement:

> ReleaseProof freezes the evidence-equivalence policy inside each human review, so a later runtime cannot silently reinterpret historical authority under new tolerance or normalization defaults.

Short memory hook:

> The human decision carries its own rules of continued validity.
