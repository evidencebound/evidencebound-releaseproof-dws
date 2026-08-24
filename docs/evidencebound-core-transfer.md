# EvidenceBound Core Transfer Boundary

## Decision

ReleaseProof should contribute only generic human-control primitives to EvidenceBound Core. The transfer is based on ReleaseProof requirements and Nutrient field feedback, not on copying OntoGuard product mechanisms.

## Candidate core primitives

### 1. Evidence identity separate from integrity

Use a small typed identity for the business evidence a decision depends on:

- source/logical artifact ID;
- page or source segment;
- field/claim path;
- normalized value;
- bounded location/context.

Keep SHA-256 or other cryptographic digests separately for integrity and provenance.

### 2. Stable claim/finding identity

A claim/finding ID should identify the logical issue, not a specific extraction payload. Evidence revisions update the binding while preserving the logical ID when the same issue is being reconsidered.

### 3. Authority binding

A human decision should bind to:

- logical claim/finding;
- exact semantic evidence set;
- policy version;
- reviewer identity;
- decision and rationale.

Historical authority is not automatically current authority.

### 4. Deterministic equivalence policy

Evidence equivalence must be explicit and testable. Different evidence classes can define exact or bounded comparison policies. ReleaseProof uses page + field path + normalized value + bounding-box tolerance. Other EvidenceBound domains can define their own typed equivalence without introducing an LLM matcher.

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
3. invalidate authority whose evidence/policy dependency no longer reproduces;
4. preserve independent authority;
5. require fresh review at the boundary where equivalence cannot be proven.

This is a Human Control Plane primitive: preserve capability while retaining correction and revocation authority.

## Explicit non-goals

- Do not copy OntoGuard ontology schemas, algorithms, policy language, implementation details, or proprietary product behavior.
- Do not claim OntoGuard novelty as EvidenceBound novelty.
- Do not add semantic-web infrastructure merely to use the word ontology.
- Do not make LLM similarity authoritative for evidence equivalence.
- Do not infer relationships that are not represented by explicit evidence or policy contracts.

## Recommended Core experiment

Before merging these concepts into EvidenceBound Core, implement one small generic module with `EvidenceIdentity`, `AuthorityBinding`, typed dependency edges, deterministic equivalence, and blast-radius calculation. Benchmark it against the existing whole-artifact invalidation behavior on at least two EvidenceBound workflows. Keep it only if it reduces unnecessary invalidation without allowing stale authority to survive a material correction.
