---
catalog_schema_version: "1.0"
case_id: R2-THERMOELASTIC-OFFDIAG-001
title: "Restore Missing Off-Diagonal Jacobian"
case_kind: atomic
track: REPAIR
subcategory: R2
physics_domains:
  - coupled_engineering_systems
  - thermal_energy_transport
  - solid_mechanics
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
  - r2
---

# Restore Missing Off-Diagonal Jacobian

## Benchmark purpose

This case is a planned atomic benchmark for **R2 — Residual, Jacobian, and coupling repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Restore Missing Off-Diagonal Jacobian**, exercises the R2 capability.

## What this case tests

**R2 — Residual, Jacobian, and coupling repair.**

- Jacobian verification passes;
- nonlinear convergence improves to the gold behavior;
- temperature, displacement, and stress quantities of interest agree with reference values;
- no governing equations or BCs are changed.

Capabilities outside R2 are intentionally excluded from the score.

## Starting information

The residual contains temperature-mechanics coupling, but the corresponding off-diagonal Jacobian derivative or coupling is missing or incorrect.

## Required output

Restore the missing derivative/coupling.

## Permitted actions

Jacobian/coupling implementation only.

## Prohibited actions

Do not modify governing physics, materials, boundary conditions, outputs, or layers outside the authorized edit scope.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only R2.


## Case construction

Develop this synthetic case from `THERMOELASTIC-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- Jacobian verification passes;
- nonlinear convergence improves to the gold behavior;
- temperature, displacement, and stress quantities of interest agree with reference values;
- no governing equations or BCs are changed.

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

- Planned public case (not created): `benchmark/public/cases/R2-THERMOELASTIC-OFFDIAG-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R2-THERMOELASTIC-OFFDIAG-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R2-THERMOELASTIC-OFFDIAG-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
