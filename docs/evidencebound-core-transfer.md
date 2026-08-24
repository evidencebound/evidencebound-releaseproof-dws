# EvidenceBound Core Transfer Boundary

## Decision

ReleaseProof should contribute only generic human-control primitives to EvidenceBound Core. The transfer is based on independently developed ReleaseProof requirements and Nutrient field feedback, not on copying OntoGuard product mechanisms.

The strongest new candidate is not a general ontology layer. It is a much smaller control primitive: **human authority carries the exact policy under which its continued validity may later be evaluated**.

## Candidate core primitives

### 1. Evidence identity separate from integrity

Use a small typed identity for the business evidence a decision depends on:

- source/logical artifact ID;
- page or source segment;
- field/claim path;
- normalized value;
- bounded location/context;
- explicit normalization version.

Keep SHA-256 or other cryptographic digests separately for integrity and provenance.

### 2. Stable claim/finding identity

A claim/finding ID should identify the logical issue, not a specific extraction payload. Evidence revisions update the binding while preserving the logical ID when the same issue is being reconsidered.

### 3. Frozen authority binding

A human decision should bind to:

- logical claim/finding;
- exact semantic evidence set;
- reviewer identity;
- decision and rationale;
- the exact equivalence policy under which authority was granted.

The equivalence policy itself should be immutable and versioned. ReleaseProof currently freezes:

- policy version;
- bbox tolerance;
- value-normalization version;
- bbox metric version.

`AuthorityBinding` should cryptographically commit to both evidence and policy. Historical authority is never automatically reinterpreted under a later runtime's defaults.

### 4. Deterministic equivalence policy

Evidence equivalence must be explicit and testable. Different evidence classes can define exact or bounded comparison policies. ReleaseProof uses page + field path + normalized value + bounding-box tolerance. Other EvidenceBound domains can define their own typed equivalence without introducing an LLM matcher.

Critical migration rule:

```text
known historical policy -> evaluate under that exact policy
unsupported historical policy -> REVIEW_REQUIRED / fail closed
legacy authority with no recorded policy -> exact historical binding only
```

This prevents silent policy drift. A later software release cannot broaden an old approval merely by changing a default tolerance or normalization algorithm.

### 5. Typed dependency edges

A minimal dependency graph can use ordinary typed records, for example:

- `grounds(evidence, claim)`
- `reviewed_by(claim, review)`
- `governs(policy, claim_or_action)`
- `authorizes(review, action)`
- `derived_from(claim, upstream_claim)`

These edges are for correction propagation and blast-radius calculation. They do not require RDF, OWL, SPARQL, a graph database, embeddings, or ontology inference.

### 6. Selective invalidation

On correction or evidence change:

1. identify changed evidence identities;
2. traverse only explicit downstream dependencies;
3. evaluate historical authority under its frozen policy;
4. invalidate authority whose evidence/policy dependency no longer reproduces;
5. preserve independent authority;
6. require fresh review where equivalence cannot be proven or the historical policy cannot be executed safely.

This is a Human Control Plane primitive: preserve capability while retaining correction and revocation authority.

## Why this is not OntoGuard-style overengineering

The proposed Core mechanism is deliberately small:

```text
EvidenceIdentity
+ FrozenEquivalencePolicy
+ AuthorityBinding
+ explicit typed dependencies
+ deterministic blast radius
```

It does not require a semantic ontology runtime or inferred world model. The system only reasons over relationships and comparison rules that EvidenceBound explicitly records.

## Explicit non-goals

- Do not copy OntoGuard ontology schemas, algorithms, policy language, implementation details, or proprietary product behavior.
- Do not claim OntoGuard novelty as EvidenceBound novelty.
- Do not add semantic-web infrastructure merely to use the word ontology.
- Do not make LLM similarity authoritative for evidence equivalence.
- Do not infer relationships that are not represented by explicit evidence or policy contracts.
- Do not describe frozen policy as legal non-repudiation or regulatory compliance by itself.

## Recommended Core experiment

Do **not** immediately generalize the ReleaseProof implementation into EvidenceBound Core production code.

First implement a small generic experiment with `EvidenceIdentity`, `FrozenEquivalencePolicy`, `AuthorityBinding`, typed dependency edges, deterministic equivalence, and the existing Core blast-radius machinery. Exercise it on at least two independent EvidenceBound workflows.

Acceptance criteria:

- fewer unnecessary invalidations than whole-artifact/version invalidation;
- zero stale-authority preservation in material-change adversarial cases;
- historical policy remains reproducible after runtime defaults change;
- unknown/unsupported historical policy fails closed;
- no LLM or ontology inference is required for the authoritative decision path.

Keep the primitive only if those tests hold. Until a second workflow validates the abstraction, ReleaseProof remains the reference implementation rather than evidence that the generic Core design is proven.
