---
catalog_schema_version: "1.0"
case_id: R1-THERMAL-BOUNDARY-REF-001
title: "Repair Invalid Radiation Boundary Reference"
case_kind: atomic
track: REPAIR
subcategory: R1
physics_domains:
  - thermal_energy_transport
difficulty: L1
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
moose_validation_required: true
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - seed-case
  - repair
  - r1
---

# Repair Invalid Radiation Boundary Reference

## Benchmark purpose

This case is a planned atomic benchmark for **R1 — HIT, schema, and reference repair**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Repair Invalid Radiation Boundary Reference**, exercises the R1 capability.

## What this case tests

**R1 — HIT, schema, and reference repair.**

- minimal patch;
- parser passes;
- schema passes;
- references resolve;
- authoritative bounded execution succeeds;
- physics and solver configuration remain unchanged.

Capabilities outside R1 are intentionally excluded from the score.

## Starting information

The radiative boundary condition references a nonexistent boundary named:

```text
radiating_surface
```

The correct boundary identifier is supplied in the diagnosis/evidence.

## Required output

Make the minimum correction required to resolve the invalid reference.

## Permitted actions

Boundary/reference wiring only.

## Prohibited actions

Do not modify governing physics, materials, boundary conditions, outputs, or layers outside the authorized edit scope.

## Isolation rationale

The root cause is already known. The only scored capability is MOOSE syntax/reference repair.


## Case construction

Develop this synthetic case from `THERMAL-RADIATION-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

- minimal patch;
- parser passes;
- schema passes;
- references resolve;
- authoritative bounded execution succeeds;
- physics and solver configuration remain unchanged.

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

- Planned public case (not created): `benchmark/public/cases/R1-THERMAL-BOUNDARY-REF-001/`
- Planned private evaluator (not created): `benchmark/private/cases/R1-THERMAL-BOUNDARY-REF-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/R1-THERMAL-BOUNDARY-REF-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
