---
catalog_schema_version: "1.0"
case_id: F3-THERMOELASTIC-MAP-001
title: "Map Coupled Thermoelastic Residuals to MOOSE"
case_kind: atomic
track: FORM
subcategory: F3
physics_domains:
  - coupled_engineering_systems
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
  - f3
---

# Map Coupled Thermoelastic Residuals to MOOSE

## Benchmark purpose

This case is a planned atomic benchmark for **F3 — MOOSE object and coupling map**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Map Coupled Thermoelastic Residuals to MOOSE**, exercises the F3 capability.

## What this case tests

**F3 — MOOSE object and coupling map.**

- registry validity;
- mathematical compatibility;
- parameter correctness;
- coupling completeness.

Capabilities outside F3 are intentionally excluded from the score.

## Starting information

The planned benchmark will provide:

- gold thermal weak form;
- gold mechanical weak form;
- variables;
- block names;
- boundary names;
- material definitions;
- a registry of permitted MOOSE objects.

## Required output

The agent must produce a term-to-object mapping identifying:

- Kernels;
- boundary conditions;
- Materials;
- Constraints if needed;
- required parameters;
- temperature-displacement couplings;
- material dependencies;
- variable references.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- weak-form derivation;
- complete input-file syntax.

## Isolation rationale

The weak form is already correct. The benchmark isolates whether the agent can translate mathematical residual terms into valid MOOSE-native objects and couplings.


## Case construction

Develop this synthetic case from `THERMOELASTIC-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- registry validity;
- mathematical compatibility;
- parameter correctness;
- coupling completeness.

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

- Planned public case (not created): `benchmark/public/cases/F3-THERMOELASTIC-MAP-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F3-THERMOELASTIC-MAP-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F3-THERMOELASTIC-MAP-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
