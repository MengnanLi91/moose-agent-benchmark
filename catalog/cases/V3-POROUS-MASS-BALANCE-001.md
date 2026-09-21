---
catalog_schema_version: "1.0"
case_id: V3-POROUS-MASS-BALANCE-001
title: "Species Mass Conservation"
case_kind: atomic
track: VERIFY
subcategory: V3
physics_domains:
  - porous_media_and_species_transport
difficulty: L3
base_problem_id: DARCY-TRACER-BASE-001
status: planned
priority: normal
owner: null
reviewers: []
source_type: synthetic
source_name: "MOOSE Agent Benchmark Seed Problems"
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - seed-case
  - verify
  - v3
---

# Species Mass Conservation

## Benchmark purpose

This case is a planned atomic benchmark for **V3 — Conservation and invariant checks**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Species Mass Conservation**, exercises the V3 capability.

## What this case tests

**V3 — Conservation and invariant checks.**

Correct conservation accounting and quantitative interpretation.

Capabilities outside V3 are intentionally excluded from the score.

## Starting information

The planned benchmark will supply an accepted transient advection-dispersion model.

## Required output

Evaluate:

```text
initial species mass
+ injected species mass
- produced species mass
- current stored species mass
```

with the correct sign convention.

- mass-balance residual;
- normalized closure metric;
- tolerance;
- conclusion.

## Permitted actions

Once implemented, run the accepted model and the controlled verification or comparison study.

## Prohibited actions

Do not change the accepted formulation or substitute model repair for the requested verification evidence.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only V3.


## Case construction

Develop this synthetic case from `DARCY-TRACER-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Correct conservation accounting and quantitative interpretation.

The executable evaluator will define objective criteria, evidence requirements, and hard gates.

## Source and provenance

Imported from the synthetic design document *MOOSE Agent Benchmark Seed Problems*. The
concrete MOOSE application, revision, source citations, licenses, and redistribution notes
remain to be recorded when the base model is selected. The case is currently a synthetic benchmark proposal.

## Implementation checklist

- [ ] Public contract and prompt written
- [ ] Required artifacts and evidence added
- [ ] Private evaluator written
- [ ] Gold and mutant development submissions added
- [ ] Manifest entry added
- [ ] Local validation passes
- [ ] Required MOOSE validation completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Planned files

These case-specific artifacts have not been created yet:

- Planned public case (not created): `benchmark/public/cases/V3-POROUS-MASS-BALANCE-001/`
- Planned private evaluator (not created): `benchmark/private/cases/V3-POROUS-MASS-BALANCE-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/V3-POROUS-MASS-BALANCE-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
The proposal used `L2-L3`; this record selects `L3` because the catalog schema requires one difficulty.
