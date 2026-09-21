---
catalog_schema_version: "1.0"
case_id: R4-PHASEFIELD-STARTUP-001
title: "Repair Stiff Phase-Field Startup"
case_kind: atomic
track: REPAIR
subcategory: R4
physics_domains:
  - phase_transformation_and_microstructure
difficulty: L2
base_problem_id: PHASEFIELD-CAHN-HILLIARD-BASE-001
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

# Repair Stiff Phase-Field Startup

## Benchmark purpose

This case is a planned atomic benchmark for **R4 — Initialization and step-control repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Repair Stiff Phase-Field Startup**, exercises the R4 capability.

## What this case tests

**R4 — Initialization and step-control repair.**

- target simulation time reached;
- nonlinear solves remain within budget;
- free-energy evolution agrees with reference behavior;
- final quantities of interest remain consistent with the gold case.

Capabilities outside R4 are intentionally excluded from the score.

## Starting information

The physical model and initial field are valid, but the first timestep is too aggressive and Newton fails before entering the intended evolution regime.

## Required output

Modify the startup strategy so the simulation reaches the target time.

## Permitted actions

- initial timestep;
- timestep-growth strategy;
- startup/continuation settings.

## Prohibited actions

- changing free energy;
- changing mobility;
- changing phase-field equations.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only R4.


## Case construction

Develop this synthetic case from `PHASEFIELD-CAHN-HILLIARD-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- target simulation time reached;
- nonlinear solves remain within budget;
- free-energy evolution agrees with reference behavior;
- final quantities of interest remain consistent with the gold case.

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

- Planned public case (not created): `benchmark/public/cases/R4-PHASEFIELD-STARTUP-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R4-PHASEFIELD-STARTUP-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R4-PHASEFIELD-STARTUP-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
