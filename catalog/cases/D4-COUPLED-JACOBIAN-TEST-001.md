---
catalog_schema_version: "1.0"
case_id: D4-COUPLED-JACOBIAN-TEST-001
title: Choose a Jacobian Test for Coupled Nonlinear Ambiguity
case_kind: atomic
track: DIAG
subcategory: D4
physics_domains:
  - coupled_engineering_systems
  - thermal_energy_transport
  - solid_and_structural_mechanics
difficulty: L3
base_problem_id: COUPLED-THERMOMECHANICAL-JACOBIAN-BASE-001
status: in_progress
priority: normal
owner: MengnanLi91
reviewers: []
source_type: discussion_derived
source_name: DIAG Benchmark Discussion-Derived Case Plan
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - diag
  - d4
  - jacobian
---

# Choose a Jacobian Test for Coupled Nonlinear Ambiguity

## Benchmark purpose

This atomic D4 case measures whether an agent chooses the next test with the highest
information gain between two plausible explanations of an unresolved coupled diagnostic.

## Problem description

A reduced temperature-displacement model has symptoms compatible with either a missing
off-diagonal Jacobian contribution or a consistent Jacobian with strongly imbalanced
residual scales.

## What this case tests

**D4 — Discriminating next test.** The score covers the selected stable action, its
information gain, and distinct predicted signatures under H1 and H2. Repair and tuning are
outside scope.

## Starting information

The participant receives a coupled-model summary, stable action IDs, observed symptoms, the
two hypotheses, and pinned validation metadata.

## Required output

Return one next action, an information-gain concept set, separate H1/H2 predictions, and an
artifact-bound observation.

## Permitted actions

- Inspect the supplied summary and diagnostic context.
- Predict the outcome of one discriminating test.

## Prohibited actions

- Modify or execute either model.
- Choose tuning actions merely to seek convergence.

## Isolation rationale

Private variants independently instantiate the two hypotheses. The public prompt exposes
only symptoms compatible with both, so success requires selecting a genuinely separating
measurement.

## Evidence available to the participant

- `artifacts/coupled-model-summary.md`
- `evidence/diagnostic-context.json`
- `evidence/run-metadata.json`

## Acceptance summary

The response must choose a finite-difference comparison of the analytic Jacobian and predict
an off-diagonal discrepancy under H1 versus an acceptable comparison with residual-scale
imbalance remaining under H2.

## Source and provenance

The case is derived from the DIAG benchmark discussion plan and reduced from a coupled
thermo-mechanical Jacobian-test pattern. On September 29, 2026, each private hypothesis was
reproduced three times with `combined-opt`, MOOSE commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`, and one process.

## Files

- [Public case contract](../../benchmark/public/cases/D4-COUPLED-JACOBIAN-TEST-001/case.yaml)
- [Prompt](../../benchmark/public/cases/D4-COUPLED-JACOBIAN-TEST-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)

## Implementation checklist

- [x] Public contract and prompt written
- [x] Required artifacts and evidence added
- [x] Private evaluator and hypothesis variants written
- [x] Gold and mutant development submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [x] Required MOOSE validation completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Open questions

Domain and benchmark-design review remain outstanding.

## Development notes

Keep private hypothesis inputs, Jacobian outputs, evaluator values, and development answers
out of the generated public participant bundle.
