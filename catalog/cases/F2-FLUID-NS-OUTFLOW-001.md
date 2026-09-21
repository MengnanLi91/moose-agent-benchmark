---
catalog_schema_version: "1.0"
case_id: F2-FLUID-NS-OUTFLOW-001
title: "Incompressible Navier-Stokes with Traction Outlet"
case_kind: atomic
track: FORM
subcategory: F2
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
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - seed-case
  - form
  - f2
---

# Incompressible Navier-Stokes with Traction Outlet

## Benchmark purpose

This case is a planned atomic benchmark for **F2 — Weak form and boundary terms**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Incompressible Navier-Stokes with Traction Outlet**, exercises the F2 capability.

## What this case tests

**F2 — Weak form and boundary terms.**

Correct residual terms, signs, integration regions, and test-function associations.

Capabilities outside F2 are intentionally excluded from the score.

## Starting information

The planned benchmark will provide:

- incompressible momentum equations;
- continuity equation;
- density and viscosity;
- inlet velocity condition;
- no-slip wall conditions;
- prescribed traction/outflow condition;
- domain and boundary labels.

## Required output

The agent must derive:

- weak momentum equation;
- weak continuity equation;
- pressure contribution;
- viscous term after integration by parts;
- boundary traction term;
- correct test-function associations.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- selecting the physical formulation;
- choosing MOOSE objects;
- input syntax.

## Isolation rationale

The strong form is fixed. The benchmark measures weak-form reasoning, especially pressure, viscous integration by parts, and the natural traction boundary term.


## Case construction

Develop this synthetic case from `INCOMPRESSIBLE-FLOW-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Correct residual terms, signs, integration regions, and test-function associations.

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

- Planned public case (not created): `benchmark/public/cases/F2-FLUID-NS-OUTFLOW-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F2-FLUID-NS-OUTFLOW-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F2-FLUID-NS-OUTFLOW-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
