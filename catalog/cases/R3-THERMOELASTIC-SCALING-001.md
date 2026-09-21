---
catalog_schema_version: "1.0"
case_id: R3-THERMOELASTIC-SCALING-001
title: "Repair Badly Scaled Coupled Solve"
case_kind: atomic
track: REPAIR
subcategory: R3
physics_domains:
  - coupled_engineering_systems
difficulty: L3
base_problem_id: THERMOELASTIC-BASE-001
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

# Repair Badly Scaled Coupled Solve

## Benchmark purpose

This case is a planned atomic benchmark for **R3 — Solver, scaling, and nullspace repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Repair Badly Scaled Coupled Solve**, exercises the R3 capability.

## What this case tests

**R3 — Solver, scaling, and nullspace repair.**

- successful bounded run;
- required convergence rate/iteration budget;
- temperature, displacement, and stress QoIs remain within tolerance;
- physics, BCs, materials, and outputs remain unchanged.

Capabilities outside R3 are intentionally excluded from the score.

## Starting information

Thermal and mechanical residual magnitudes differ sufficiently that the current nonlinear/linear solver configuration is ineffective.

## Required output

Improve convergence efficiency while preserving the formulation.

## Permitted actions

The agent may modify:

- residual scaling;
- nonlinear scaling;
- field decomposition;
- preconditioning;
- solver tolerances within a specified accuracy floor.

## Prohibited actions

Do not modify governing physics, materials, boundary conditions, outputs, or layers outside the authorized edit scope.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only R3.


## Case construction

Develop this synthetic case from `THERMOELASTIC-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- successful bounded run;
- required convergence rate/iteration budget;
- temperature, displacement, and stress QoIs remain within tolerance;
- physics, BCs, materials, and outputs remain unchanged.

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

- Planned public case (not created): `benchmark/public/cases/R3-THERMOELASTIC-SCALING-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R3-THERMOELASTIC-SCALING-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R3-THERMOELASTIC-SCALING-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
