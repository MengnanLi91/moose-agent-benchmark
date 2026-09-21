---
catalog_schema_version: "1.0"
case_id: D3-THERMAL-RADIATION-SIGN-001
title: "Localize Runaway Heating to Radiation BC"
case_kind: atomic
track: DIAG
subcategory: D3
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
  - diag
  - d3
---

# Localize Runaway Heating to Radiation BC

## Benchmark purpose

This case is a planned atomic benchmark for **D3 — Root-cause localization**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Localize Runaway Heating to Radiation BC**, exercises the D3 capability.

## What this case tests

**D3 — Root-cause localization.**

Cause class and precise location.

Capabilities outside D3 are intentionally excluded from the score.

## Starting information

The planned benchmark will supply:

- immutable nonlinear heat-transfer input;
- output showing surface temperature increasing when radiation should cool the body;
- heat-flow telemetry;
- upstream diagnosis establishing the relevant failure mechanism.

## Required output

The agent must identify:

- root-cause family;
- exact faulty boundary-condition object or equation term;
- artifact-bound evidence.

## Permitted actions

Once implemented, inspect the supplied immutable artifacts and participant-visible evidence.

## Prohibited actions

- editing the BC;
- rerunning a repaired model.

## Isolation rationale

Upstream truth is supplied and downstream work is excluded so the case scores only D3.


## Case construction

Develop this synthetic case from `THERMAL-RADIATION-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Cause class and precise location.

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

- Planned public case (not created): `benchmark/public/cases/D3-THERMAL-RADIATION-SIGN-001/`
- Planned private evaluator (not created): `benchmark/private/cases/D3-THERMAL-RADIATION-SIGN-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/D3-THERMAL-RADIATION-SIGN-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
