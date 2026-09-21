---
catalog_schema_version: "1.0"
case_id: D4-THERMAL-JACOBIAN-TEST-001
title: "Bad Jacobian or Poor Initial Guess?"
case_kind: atomic
track: DIAG
subcategory: D4
physics_domains:
  - thermal_energy_transport
difficulty: L3
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
  - diag
  - d4
---

# Bad Jacobian or Poor Initial Guess?

## Benchmark purpose

This case is a planned atomic benchmark for **D4 — Discriminating next test**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Bad Jacobian or Poor Initial Guess?**, exercises the D4 capability.

A strongly nonlinear $T^4$ radiation problem stagnates during Newton iteration.

## What this case tests

**D4 — Discriminating next test.**

Expected information gain and predicted signatures.

Capabilities outside D4 are intentionally excluded from the score.

## Starting information

1. The analytic/automatic Jacobian is inconsistent with the residual.
2. The Jacobian is correct, but the initial state is poor.

## Required output

The agent must choose the next test and predict outcomes under both hypotheses.

## Permitted actions

- directional finite-difference Jacobian check;
- restart from an improved initial state;
- residual/Jacobian comparison.

## Prohibited actions

Do not repair or modify the immutable benchmark workspace.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only D4.


## Case construction

Develop this synthetic case from `THERMAL-RADIATION-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Expected information gain and predicted signatures.

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

- Planned public case (not created): `benchmark/public/cases/D4-THERMAL-JACOBIAN-TEST-001/`
- Planned private evaluator (not created): `benchmark/private/cases/D4-THERMAL-JACOBIAN-TEST-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/D4-THERMAL-JACOBIAN-TEST-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
