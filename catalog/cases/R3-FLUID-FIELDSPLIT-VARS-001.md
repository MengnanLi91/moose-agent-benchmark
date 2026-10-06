---
catalog_schema_version: "1.0"
case_id: R3-FLUID-FIELDSPLIT-VARS-001
title: Repair an Incomplete Nested Field-Split Partition
case_kind: atomic
track: REPAIR
subcategory: R3
physics_domains:
  - fluid_dynamics
  - species_transport
difficulty: L2
base_problem_id: COUPLED-STOKES-SPECIES-FSP-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: discussion_derived
source_name: MOOSE Discussion 32033
source_url: https://github.com/idaholab/moose/discussions/32033
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - repair
  - r3
  - fieldsplit
  - preconditioning
---

# Repair an Incomplete Nested Field-Split Partition

## Benchmark purpose

This atomic R3 case measures repair of variable ownership in a nested field-split solver
without permitting a solver replacement or physics change.

## Participant contract

The participant preserves the `fluid + concentration`, then `velocity + pressure` hierarchy
and changes only field-split ownership plus mechanically required split wiring.

## Isolation and acceptance

Protected gates use pinned HIT queries to verify complete, disjoint child ownership, run input
validation and bounded execution, reject direct-LU substitution, and preserve flow and
concentration reference quantities.

## Source and provenance

The mechanism is adapted from MOOSE Discussion 32033 and reproduced on commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`; the transported-species fixture is an original
reduction.

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

- [Public contract](../../benchmark/public/cases/R3-FLUID-FIELDSPLIT-VARS-001/case.yaml)
- [Prompt](../../benchmark/public/cases/R3-FLUID-FIELDSPLIT-VARS-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)
