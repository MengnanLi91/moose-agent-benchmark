---
catalog_schema_version: "1.0"
case_id: F4-POROUS-TRACER-001
title: "Assemble Saturated Darcy + Tracer Model"
case_kind: atomic
track: FORM
subcategory: F4
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
  - form
  - f4
---

# Assemble Saturated Darcy + Tracer Model

## Benchmark purpose

This case is a planned atomic benchmark for **F4 — Input assembly and parameter wiring**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Assemble Saturated Darcy + Tracer Model**, exercises the F4 capability.

## What this case tests

**F4 — Input assembly and parameter wiring.**

- correct block structure;
- correct references;
- correct variable couplings;
- correct material-property wiring;
- correct requested outputs;
- executable validation.

Capabilities outside F4 are intentionally excluded from the score.

## Starting information

The planned benchmark will provide:

- complete Darcy-flow formulation;
- passive tracer formulation;
- gold weak forms;
- intended MOOSE object plan;
- mesh blocks;
- material properties;
- inlet pressure/flow data;
- inlet concentration history;
- outlet quantity of interest;
- execution settings.

## Required output

The agent must build a fully wired executable MOOSE input.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- reformulating the physics;
- alternative object selection;
- fault diagnosis.

## Isolation rationale

The case stresses input assembly across multiple coupled fields without requiring upstream modeling decisions.


## Case construction

Develop this synthetic case from `DARCY-TRACER-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- correct block structure;
- correct references;
- correct variable couplings;
- correct material-property wiring;
- correct requested outputs;
- executable validation.

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

- Planned public case (not created): `benchmark/public/cases/F4-POROUS-TRACER-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F4-POROUS-TRACER-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F4-POROUS-TRACER-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
