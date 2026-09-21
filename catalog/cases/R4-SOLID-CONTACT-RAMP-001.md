---
catalog_schema_version: "1.0"
case_id: R4-SOLID-CONTACT-RAMP-001
title: "Repair Contact/Load Startup"
case_kind: atomic
track: REPAIR
subcategory: R4
physics_domains:
  - solid_mechanics
  - contact_mechanics
difficulty: L3
base_problem_id: CONTACT-MECHANICS-BASE-001
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
  - repair
  - r4
---

# Repair Contact/Load Startup

## Benchmark purpose

This case is a planned atomic benchmark for **R4 — Initialization and step-control repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Repair Contact/Load Startup**, exercises the R4 capability.

A contact problem closes abruptly when the full mechanical load is applied in the first increment.

## What this case tests

**R4 — Initialization and step-control repair.**

- simulation reaches full prescribed load;
- final displacement agrees with gold;
- reaction force agrees with gold;
- contact force/status agrees with gold;
- contact law, friction, materials, and final load remain unchanged.

Capabilities outside R4 are intentionally excluded from the score.

## Starting information

The contact formulation and material model are correct. Failure is caused by the load/startup strategy.

## Required output

Design a stable load application strategy.

## Permitted actions

- load ramp;
- timestep/load increments;
- continuation parameters;
- startup controls.

## Prohibited actions

Do not modify governing physics, materials, boundary conditions, outputs, or layers outside the authorized edit scope.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only R4.


## Case construction

Develop this synthetic case from `CONTACT-MECHANICS-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- simulation reaches full prescribed load;
- final displacement agrees with gold;
- reaction force agrees with gold;
- contact force/status agrees with gold;
- contact law, friction, materials, and final load remain unchanged.

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

- Planned public case (not created): `benchmark/public/cases/R4-SOLID-CONTACT-RAMP-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R4-SOLID-CONTACT-RAMP-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R4-SOLID-CONTACT-RAMP-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
