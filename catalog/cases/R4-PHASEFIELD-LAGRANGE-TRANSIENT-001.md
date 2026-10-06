---
catalog_schema_version: "1.0"
case_id: R4-PHASEFIELD-LAGRANGE-TRANSIENT-001
title: Recover a Transient Lagrange-Constraint Solver Breakdown
case_kind: atomic
track: REPAIR
subcategory: R4
physics_domains:
  - phase_transformation_and_microstructure
difficulty: L3
base_problem_id: MULTIPHASE-LAGRANGE-CONSTRAINT-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: discussion_derived
source_name: MOOSE Discussion 28937
source_url: https://github.com/idaholab/moose/discussions/28937
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - repair
  - r4
  - phase-field
  - lagrange-constraint
---

# Recover a Transient Lagrange-Constraint Solver Breakdown

## Benchmark purpose

This atomic R4 case measures a source-faithful repair of a transient Lagrange-constraint
breakdown, not an unsupported first-step startup failure.

## Participant contract

The supplied model advances before failing. The participant changes exactly two values: the
multiplier initial condition and constraint regularization. Solver, timestep, phase fields,
free energies, and mesh are frozen.

## Isolation and acceptance

Protected gates require both small nonzero values, progress beyond the faulty failure time,
bounded completion, removal of the SUBPC-equivalent failure, phase-sum preservation, and
agreement with early reference evolution.

## Source and provenance

The mechanism is adapted from MOOSE Discussion 28937 and reproduced on commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`; the fixture is an original reduction.

## Implementation checklist

- [x] Public contract, prompt, diagnosis, and failure evidence added
- [x] Private fixture, reference repair, gates, and required mutants added
- [x] Manifest entry added as disabled for authoring validation
- [x] Three-run records and tolerance derivation committed
- [x] Gold and mutant scoring fixtures generated
- [x] Case enabled after discrimination passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/R4-PHASEFIELD-LAGRANGE-TRANSIENT-001/case.yaml)
- [Prompt](../../benchmark/public/cases/R4-PHASEFIELD-LAGRANGE-TRANSIENT-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)
