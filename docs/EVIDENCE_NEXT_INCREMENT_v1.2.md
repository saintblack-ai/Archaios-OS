# Evidence envelope increment — v1.2

Date: 2026-10-31. Status: **standalone draft envelope; not intake-ready**.
Base: `f01eea512817322b334da5ec3e6f001f3d2731cf` in a disposable checkout.
Candidate: `Archaios-OS.patch` from `ARCHAIOS_Infrastructure_Review_v1.1.zip`,
plus this draft-only strict intelligence envelope increment.

The owner accepts the patch as a candidate, not as production readiness or a
house-standard adoption. The validator remains disconnected from intelligence
consumers, databases, publishing, scheduled jobs and orchestration. No agent
imports or consumers were changed. Structural acceptance never verifies or
promotes a claim, source, measurement, reviewer or scientific result.

## Implemented draft schema

`archaios_core/intelligence_envelope.py` exposes the pure
`validate_intelligence_record(record) -> list[str]` function. It returns errors
without changing the record. The version is `archaios.intelligence.draft.v1`;
`recordKind` must be `INTELLIGENCE`. All listed fields are required; only fields
explicitly permitting unknowns may be null. Unknown fields are rejected.

| Field group | Fields and checks |
| --- | --- |
| Envelope | `recordKind`, `schemaVersion`, `recordId`, `domain`, `store`, mandatory `mode`; nonempty `claim`, `source`, `counterevidence`, `provenance`; declared `category` and `confidence`. |
| Independent calendar dates | `eventDate`, `publishedDate`, `reviewDate`: real YYYY-MM-DD calendar dates or null. |
| Placement | `placement` is PLACED or UNPLACED. PLACED requires numeric finite `latitude` in [-90,90] and `longitude` in [-180,180]. Booleans and coercible strings fail; valid zero survives unchanged. UNPLACED requires both coordinates explicitly null. No automatic (0,0), map insertion or unplaced UI is implemented. |
| Counts | Only `incidentCount`: nonnegative integer or null; booleans, fractional/negative/string counts fail. Strict fields plus recursive normalized-key deny-list reject structured fatality/casualty/death/injury fields and aliases. This is not a natural-language claim classifier and does not interpret arbitrary claim text as a measured quantity. |
| Source timing | `observedAt`, `sourceUpdatedAt`, `retrievedAt`: independent timestamp instants with known UTC offsets, or null. Observation/update cannot be later than retrieval. `sourceCadence` is positive integer seconds or null. Unknowns stay null, never synthesized. |
| Connectivity/freshness | `connectivity`: connected/disconnected/error/unknown. `freshnessStatus`: current/delayed/stale/unknown/error. Assessed freshness needs valid update/retrieval/cadence; otherwise unknown/error. Labels remain declarations: no fetch, current-clock comparison, invented threshold or corroboration inference. |
| Evidence/claims | `evidenceSources`: nonempty list of exact `{sourceId,citation,originId}` objects; source IDs unique in record; HTTP(S) citations with host and no embedded username/password. `coreClaims`: nonempty text list. `independenceRationale`: explicit assessment or unknown explanation. |
| Review declaration | `reviewStatus`: UNREVIEWED or INDEPENDENTLY_REVIEWED. `sourceAssessment`: exact `{status,rationale,sourceIds}`, UNASSESSED/ASSESSED status, nonempty rationale and exact unique evidence-source coverage. |
| Reviewer declaration | `reviewerIdentity`: null or exact nonempty `{id,issuer}`. Reviewed records need `assessedBy` matching identity ID and offset `assessedAt`. UNREVIEWED requires all three null and source assessment UNASSESSED. These declarations are not authenticated identities. |

All modes have explicit partitions:

| Mode | Domain | Store | ID prefix |
| --- | --- | --- | --- |
| LIVE | intelligence | intelligence/live | intelligence: |
| CACHED | intelligence | intelligence/cached | intelligence: |
| DEMO | demo | demo/events | demo: |
| SIMULATION | simulation | simulation/events | simulation: |

Mismatched partitions or prefixes fail. DEMO/SIMULATION must stay Unassessed and
cannot declare category VERIFIED. A QX/MEASUREMENT `claimType` cannot enter this
strict intelligence schema. No conversion or movement between stores occurs.
Declared VERIFIED category/confidence requires complete review declarations and
two distinct declared origin IDs. This cannot establish actual independence:
echoed sources can be mislabeled by an author. Structural acceptance does not
apply or approve labels.

The original QX draft stays compatible with its fixture and seven tests.
`validate_record` dispatches explicit intelligence kinds, known intelligence
prefixes and intelligence-only fields to the strict schema. Legacy generic
validation cannot determine domain from prose. A future intelligence consumer
must call `validate_intelligence_record` and require explicit kind, never accept
a generic structural pass as intelligence admission. Arbitrary prose may still
pass legacy generic evidence checks; no intelligence consumer is connected.

## Durable boundaries specified, not implemented

`archaios_core/evidence_boundaries.py` has dataclasses and a Python `Protocol`
only: no store implementation, network call, registration, orchestration import
or claim promotion.

- `EvidencePartition` names domain, store and mode.
- `ReviewAuditEntry` records ID/version, actor/identity issuer, time,
  action/rationale, prior/proposed labels and source-assessment reference.
- `DraftEvidenceRepository.insert_new` specifies atomic global ID reservation,
  partitioned insert and audit append. IDs must stay unique across stores,
  batches, imports, concurrent writers and tombstones.
- `append_review` specifies authenticated/authorized review, expected-version
  checks and append-only history. Proposed labels are not applied automatically.

Method signatures guarantee none of this. A future adapter must prove durable
uniqueness, authorization, segregation of data/counters/search and audit
preservation at actual storage/identity boundaries. Within-batch duplicate
checking is not persistent uniqueness. Actor/issuer strings are not proof of
identity. No production database was created or used.

## Verification and limits

Run from repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m archaios_core.evidence research/fixtures/qx-concept.json
python3 -m archaios_core.evidence research/fixtures/intelligence-draft.json
git diff --check
```

Results: **21 tests passed** (7 original QX + 14 intelligence); both fixture CLIs
passed with `scope=draft_structural_validation_only`; whitespace check passed.
A bounded malformed-input probe of 297 field/type combinations returned errors
without exceptions. No Python build step is defined; these standard-library
modules require no new dependencies.

Tests cover valid zero/bounds, unplaced/nulls, missing mode/schema/kind,
mode/store/prefix mismatches, invalid counts, unknown/nested forbidden fields,
invalid freshness metadata, source/assessment coverage, reviewer declarations,
label non-mutation, simulated-measurement fencing and batch duplicates. Accepted
fixtures are synthetic; rejected test values are never ingested factual records.

No live data quality, source licensing, authenticated reviewer identity, durable
storage, adversarial semantic/source assessment, independent review, hardware
or research efficacy is established. Unknown freshness must display Not supplied
in a future UI; no UI or event-age rendering is implemented.

## Next review gate

Review strict schema, data-retention/audit policy and adapter protocol before
house-standard adoption. Define source-specific freshness thresholds,
current-clock age calculation, clock-skew policy and authorized human review.
Separately authorize an adapter test environment for concurrent uniqueness,
cross-store quarantine and reviewer authorization tests. No production consumer,
database, publishing or orchestration integration is authorized. Keep this PR
separate from the API repair.

QLE retains its owner-authored meaning: Quandrix Light Equation, a philosophical
and systems-engineering composite, not a physical law or evidence confidence
metric. This validator neither evaluates nor redefines it.

Source note: the owner workspace document **QLE-001 — The Quandrix Light
Equation**, framework version 1.0, was directly read during this review. It is an
external owner-workspace authority, not a file claimed to exist in this core
checkout. No private personal context or broader workspace content is copied.
