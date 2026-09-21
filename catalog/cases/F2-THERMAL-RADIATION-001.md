---
catalog_schema_version: "1.0"
case_id: F2-THERMAL-RADIATION-001
title: "Weak Form of Nonlinear Radiation Problem"
case_kind: atomic
track: FORM
subcategory: F2
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
  - f2
---

# Weak Form of Nonlinear Radiation Problem

## Benchmark purpose

This case is a planned atomic benchmark for **F2 — Weak form and boundary terms**. It measures
the requested behavior without awarding cross-credit for upstream or downstream work.

> [!NOTE]
> This is a planning record only. The referenced public/private case directories, inputs,
> logs, evaluator, and submission fixtures have not been created yet.

## Problem description

This planned atomic case, **Weak Form of Nonlinear Radiation Problem**, exercises the F2 capability.

## What this case tests

**F2 — Weak form and boundary terms.**

Symbolic or term-level equivalence to the gold weak residual.

Capabilities outside F2 are intentionally excluded from the score.

## Starting information

The planned benchmark will provide the canonical transient heat equation,

$$
\rho c_p \frac{\partial T}{\partial t}
-
\nabla \cdot \left(k(T)\nabla T\right)
=
Q,
$$

along with the nonlinear radiative boundary law,

$$
q_{\mathrm{rad}}
=
\epsilon \sigma
\left(
T^4 - T_\infty^4
\right),
$$

plus:

- domain labels;
- boundary labels;
- initial condition;
- prescribed-temperature boundary;
- insulated boundaries;
- radiating boundary.

## Required output

The agent must derive the test-function residual including:

- transient volume term;
- diffusion volume term after integration by parts;
- volumetric source term;
- natural boundary term;
- nonlinear radiation boundary contribution;
- correct sign convention;
- correct test-function association.

## Permitted actions

Use the supplied upstream formulation information to produce only the requested artifact.

## Prohibited actions

- MOOSE object selection;
- input construction;
- solver configuration.

## Isolation rationale

The governing physics is already supplied. The benchmark isolates weak-form derivation and boundary-sign reasoning.


## Case construction

Develop this synthetic case from `THERMAL-RADIATION-BASE-001`. Preserve the clean reference
model. For mutation-based variants, place hidden mutation details in the private evaluator;
keep all expected answers and numeric thresholds private.

## Evidence available to the participant

- The participant-visible inputs and evidence described under Starting information.
- Concrete artifact names and captured outputs will be finalized during implementation.

## Acceptance summary

Symbolic or term-level equivalence to the gold weak residual.

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

- Planned public case (not created): `benchmark/public/cases/F2-THERMAL-RADIATION-001/`
- Planned private evaluator (not created): `benchmark/private/cases/F2-THERMAL-RADIATION-001/`
- Planned development fixtures (not created): `benchmark/example-submissions/F2-THERMAL-RADIATION-001*.json`
- Planned manifest registration (not added): entry in `benchmark/manifest.yaml`

## Open questions

Finalize the reference model, participant-visible artifacts, objective evaluator, and
reviewed tolerances before implementation begins.

## Development notes

This planned record captures the seed design only; it is not yet a runnable benchmark case.
