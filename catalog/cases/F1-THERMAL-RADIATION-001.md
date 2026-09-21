---
catalog_schema_version: "1.0"
case_id: F1-THERMAL-RADIATION-001
title: "Radiatively Cooled Heated Plate"
case_kind: atomic
track: FORM
subcategory: F1
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: THERMAL-RADIATION-BASE-001
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

# Radiatively Cooled Heated Plate

## Benchmark purpose

This case is a planned atomic benchmark for **F1 — Physics specification and constitutive closure**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Radiatively Cooled Heated Plate**, exercises the F1 capability.

A steel plate contains volumetric heat generation. Its thermal conductivity is temperature dependent. One boundary is maintained at a prescribed temperature, two boundaries are insulated, and one boundary radiates heat to the environment.

## What this case tests

**F1 — Physics specification and constitutive closure.**

Element-level agreement with the gold physics specification.

Capabilities outside F1 are intentionally excluded from the score.

## Starting information

- engineering description;
- geometry;
- material properties;
- temperature-dependent thermal conductivity;
- ambient temperature;
- emissivity;
- volumetric heat-generation rate;
- requested surface-temperature and heat-loss quantities of interest.

## Required output

The agent must identify:

- primary variable;
- governing energy equation;
- constitutive relation for heat conduction;
- radiative heat-transfer law;
- initial condition;
- prescribed-temperature boundary condition;
- insulated boundary conditions;
- radiative boundary condition;
- required quantities of interest.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- weak-form derivation;
- MOOSE object selection;
- MOOSE input syntax.

## Isolation rationale

The task tests whether the agent can translate an engineering description into a complete mathematical and physical specification. The use of nonlinear radiation requires correct treatment of absolute temperature and the Stefan-Boltzmann law without requiring any MOOSE-specific implementation knowledge.


## Case construction

Develop this synthetic case from `THERMAL-RADIATION-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Element-level agreement with the gold physics specification.

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

- Planned public case (not created): `benchmark/public/cases/F1-THERMAL-RADIATION-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F1-THERMAL-RADIATION-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F1-THERMAL-RADIATION-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
