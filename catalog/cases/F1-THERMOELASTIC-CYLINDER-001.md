---
catalog_schema_version: "1.0"
case_id: F1-THERMOELASTIC-CYLINDER-001
title: "Heated Pressurized Thick Cylinder"
case_kind: atomic
track: FORM
subcategory: F1
physics_domains:
  - coupled_engineering_systems
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
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - seed-case
  - form
  - f1
---

# Heated Pressurized Thick Cylinder

## Benchmark purpose

This case is a planned atomic benchmark for **F1 — Physics specification and constitutive closure**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Heated Pressurized Thick Cylinder**, exercises the F1 capability.

An axisymmetric thick-walled cylinder experiences internal pressure and a radial temperature gradient. The material is linear elastic and undergoes thermal expansion.

## What this case tests

**F1 — Physics specification and constitutive closure.**

Completeness and correctness of the coupled physics specification.

Capabilities outside F1 are intentionally excluded from the score.

## Starting information

- inner and outer radii;
- elastic modulus;
- Poisson ratio;
- thermal-expansion coefficient;
- thermal conductivity;
- internal pressure;
- inner and outer thermal boundary conditions;
- requested bore-displacement and hoop-stress quantities of interest.

## Required output

The agent must identify:

- temperature variable;
- displacement variables appropriate for the axisymmetric formulation;
- heat-conduction equation;
- mechanical equilibrium equations;
- elastic constitutive relation;
- thermal-strain contribution;
- mechanical boundary conditions;
- thermal boundary conditions;
- initial conditions;
- requested quantities of interest.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- weak form;
- MOOSE object names;
- input syntax.

## Isolation rationale

The benchmark requires constitutive closure and coupling identification without requiring weak-form or MOOSE-specific implementation reasoning.


## Case construction

Develop this synthetic case from `THERMOELASTIC-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Completeness and correctness of the coupled physics specification.

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

- Planned public case (not created): `benchmark/public/cases/F1-THERMOELASTIC-CYLINDER-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F1-THERMOELASTIC-CYLINDER-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F1-THERMOELASTIC-CYLINDER-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
