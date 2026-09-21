---
catalog_schema_version: "1.0"
case_id: V1-THERMAL-MMS-001
title: "Nonlinear Heat-Conduction MMS"
case_kind: atomic
track: VERIFY
subcategory: V1
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: THERMAL-MMS-BASE-001
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
  - verify
  - v1
---

# Nonlinear Heat-Conduction MMS

## Benchmark purpose

This case is a planned atomic benchmark for **V1 — Exact-solution and MMS verification**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Nonlinear Heat-Conduction MMS**, exercises the V1 capability.

## What this case tests

**V1 — Exact-solution and MMS verification.**

- correct norm;
- correct observed order;
- reproducible quantitative evidence;
- correct interpretation.

Capabilities outside V1 are intentionally excluded from the score.

## Starting information

The planned benchmark will provide:

- accepted executable MOOSE model;
- manufactured temperature field $T^*(x,y,t)$;
- precomputed forcing function;
- precomputed boundary expressions;
- expected element order;
- mesh-refinement sequence.

## Required output

The agent must:

1. run the supplied mesh sequence;
2. compute the spatial $L^2$ error;
3. estimate the observed order of convergence;
4. compare against the expected discretization order;
5. issue an implementation-verification conclusion.

## Permitted actions

Once implemented, run the accepted model and the controlled verification or comparison study.

## Prohibited actions

Do not change the accepted formulation or substitute model repair for the requested verification evidence.

## Isolation rationale

The manufactured forcing term is supplied. The agent is not asked to derive it.


## Case construction

Develop this synthetic case from `THERMAL-MMS-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- correct norm;
- correct observed order;
- reproducible quantitative evidence;
- correct interpretation.

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

- Planned public case (not created): `benchmark/public/cases/V1-THERMAL-MMS-001/`
- Planned private evaluator (not created): `benchmark/private/cases/V1-THERMAL-MMS-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/V1-THERMAL-MMS-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
