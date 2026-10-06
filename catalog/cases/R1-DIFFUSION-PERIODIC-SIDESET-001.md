---
catalog_schema_version: "1.0"
case_id: R1-DIFFUSION-PERIODIC-SIDESET-001
title: Repair a Partially Overlapping Periodic Sideset
case_kind: atomic
track: REPAIR
subcategory: R1
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: DIFFUSION-PERIODIC-TRANSLATION-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: discussion_derived
source_name: MOOSE Discussion 33207
source_url: https://github.com/idaholab/moose/discussions/33207
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - repair
  - r1
  - periodic-boundary
  - sideset
---

# Repair a Partially Overlapping Periodic Sideset

## Benchmark purpose

This atomic R1 case measures a minimal structural repair to a periodic sideset and its
reference after the root cause has already been supplied.

## Participant contract

The participant receives an original reduced diffusion fixture whose right periodic boundary
contains unmatched upper faces. The submitted input may only create or restrict the matching
right sideset and update the periodic reference.

## Isolation and acceptance

Protected gates compare normalized HIT paths, run input validation and bounded execution, and
check translated point equality plus reference integral and average values. Physics,
translation, solver settings, and outputs are frozen.

## Source and provenance

The failure mechanism is adapted from MOOSE Discussion 33207 and reproduced on commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`; no discussion attachment is copied.

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

- [Public contract](../../benchmark/public/cases/R1-DIFFUSION-PERIODIC-SIDESET-001/case.yaml)
- [Prompt](../../benchmark/public/cases/R1-DIFFUSION-PERIODIC-SIDESET-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)
