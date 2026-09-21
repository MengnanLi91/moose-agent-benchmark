---
catalog_schema_version: "1.0"
case_id: R3-FLUID-PRESSURE-NULLSPACE-001
title: "Repair Incompressible Pressure Nullspace Handling"
case_kind: atomic
track: REPAIR
subcategory: R3
physics_domains:
  - fluid_dynamics
difficulty: L3
base_problem_id: INCOMPRESSIBLE-FLOW-BASE-001
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
  - r3
---

# Repair Incompressible Pressure Nullspace Handling

## Benchmark purpose

This case is a planned atomic benchmark for **R3 — Solver, scaling, and nullspace repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Repair Incompressible Pressure Nullspace Handling**, exercises the R3 capability.

## What this case tests

**R3 — Solver, scaling, and nullspace repair.**

- robust convergence;
- preserved velocity field;
- preserved pressure differences;
- preserved flow-rate and pressure-drop QoIs;
- no changes to inlet/outlet physics.

Capabilities outside R3 are intentionally excluded from the score.

## Starting information

A constant-pressure nullspace is causing the linear solve failure. The governing equations and physical boundary conditions are otherwise correct.

## Required output

Implement a valid nullspace/gauge treatment.

## Permitted actions

- pressure-gauge configuration;
- nullspace treatment;
- linear solver/preconditioner settings.

## Prohibited actions

Do not modify governing physics, materials, boundary conditions, outputs, or layers outside the authorized edit scope.

## Isolation rationale

The physics is frozen and the diagnosis is supplied. Only solver/nullspace configuration may change.


## Case construction

Develop this synthetic case from `INCOMPRESSIBLE-FLOW-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- robust convergence;
- preserved velocity field;
- preserved pressure differences;
- preserved flow-rate and pressure-drop QoIs;
- no changes to inlet/outlet physics.

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

- Planned public case (not created): `benchmark/public/cases/R3-FLUID-PRESSURE-NULLSPACE-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R3-FLUID-PRESSURE-NULLSPACE-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R3-FLUID-PRESSURE-NULLSPACE-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
The proposal used `L2-L3`; this record selects `L3` because the catalog schema requires one difficulty.
