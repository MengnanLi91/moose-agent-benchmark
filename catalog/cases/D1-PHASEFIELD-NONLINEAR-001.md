---
catalog_schema_version: "1.0"
case_id: D1-PHASEFIELD-NONLINEAR-001
title: "Newton Failure Followed by Timestep Collapse"
case_kind: atomic
track: DIAG
subcategory: D1
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
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - seed-case
  - diag
  - d1
---

# Newton Failure Followed by Timestep Collapse

## Benchmark purpose

This case is a planned atomic benchmark for **D1 — Failure-stage classification**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Newton Failure Followed by Timestep Collapse**, exercises the D1 capability.

## What this case tests

**D1 — Failure-stage classification.**

Grade only the designated atomic capability.

Capabilities outside D1 are intentionally excluded from the score.

## Starting information

The planned benchmark will supply:

- valid transient phase-field input;
- solver log showing nonlinear failure;
- timestep rejection;
- repeated timestep reduction;
- final termination at minimum timestep.

## Required output

The agent must distinguish:

- earliest failed stage;
- terminal symptom.

## Permitted actions

Once implemented, inspect the supplied immutable artifacts and participant-visible evidence.

## Prohibited actions

- explaining the nonlinear failure mechanism;
- identifying the exact root cause;
- repair.

## Isolation rationale

The final log message is intentionally not the earliest failure stage.


## Case construction

Develop this synthetic case from `PHASEFIELD-CAHN-HILLIARD-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Grade only the designated atomic capability.

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

- Planned public case (not created): `benchmark/public/cases/D1-PHASEFIELD-NONLINEAR-001/`
- Planned private evaluator (not created): `benchmark/private/cases/D1-PHASEFIELD-NONLINEAR-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/D1-PHASEFIELD-NONLINEAR-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
