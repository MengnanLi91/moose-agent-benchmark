---
catalog_schema_version: "1.0"
case_id: V4-FSI-TUREK-HRON-001
title: "Turek-Hron Fluid-Structure Interaction Comparison"
case_kind: atomic
track: VERIFY
subcategory: V4
physics_domains:
  - coupled_engineering_systems
  - fluid_dynamics
  - solid_mechanics
difficulty: L4
base_problem_id: FSI-TUREK-HRON-BASE-001
status: planned
priority: normal
owner: null
reviewers: []
source_type: published_benchmark
source_name: "Turek-Hron FSI benchmark"
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
  - verify
  - v4
---

# Turek-Hron Fluid-Structure Interaction Comparison

## Benchmark purpose

This case is a planned atomic benchmark for **V4 — External evidence comparison**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Turek-Hron Fluid-Structure Interaction Comparison**, exercises the V4 capability.

## What this case tests

**V4 — External evidence comparison.**

- correct observable mapping;
- quantitative agreement calculation;
- uncertainty treatment;
- evidence-qualified conclusion.

Capabilities outside V4 are intentionally excluded from the score.

## Starting information

The planned benchmark will supply:

- accepted MOOSE-based FSI model;
- benchmark geometry/specification;
- published reference values or ranges;
- requested observables.

Published Turek-Hron fluid-structure interaction benchmark data.

## Required output

The agent must:

1. map MOOSE outputs to benchmark observables;
2. compute agreement metrics;
3. account for reference uncertainty or reported ranges;
4. make a calibrated external-evidence statement.

Examples:

- beam-tip $x$-displacement;
- beam-tip $y$-displacement;
- drag;
- lift;
- oscillation quantities if appropriate.

## Permitted actions

Once implemented, run the accepted model and the controlled verification or comparison study.

## Prohibited actions

Do not change the accepted formulation or substitute model repair for the requested verification evidence.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only V4.


## Case construction

Develop this synthetic case from `FSI-TUREK-HRON-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- correct observable mapping;
- quantitative agreement calculation;
- uncertainty treatment;
- evidence-qualified conclusion.

The executable evaluator will define objective criteria, evidence requirements, and hard gates.

## Source and provenance

Imported from the synthetic design document *MOOSE Agent Benchmark Seed Problems*. The
concrete MOOSE application, revision, source citations, licenses, and redistribution notes
remain to be recorded when the base model is selected. The intended external reference is *Turek-Hron FSI benchmark*.

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

- Planned public case (not created): `benchmark/public/cases/V4-FSI-TUREK-HRON-001/`
- Planned private evaluator (not created): `benchmark/private/cases/V4-FSI-TUREK-HRON-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/V4-FSI-TUREK-HRON-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
