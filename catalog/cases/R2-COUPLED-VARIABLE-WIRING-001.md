---
catalog_schema_version: "1.0"
case_id: R2-COUPLED-VARIABLE-WIRING-001
title: Repair a Missing Coupled-Variable Declaration
case_kind: atomic
track: REPAIR
subcategory: R2
physics_domains:
  - coupled_engineering_systems
  - thermal_energy_transport
difficulty: L2
base_problem_id: COUPLED-MATERIAL-VARIABLE-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: discussion_derived
source_name: MOOSE Discussion 28157
source_url: https://github.com/idaholab/moose/discussions/28157
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - repair
  - r2
  - input-only
  - parsed-material
  - coupled-variable
---

# Repair a Missing Coupled-Variable Declaration

## Benchmark purpose

This atomic R2 case measures a minimal input-level coupling repair. A maintained
`ParsedMaterial` expression references an existing nonlinear temperature variable, but the
material omits the declaration that exposes that variable to the parser.

## Participant contract

The participant submits one complete replacement `.i` file. Only
`Materials/dependent_diffusivity/coupled_variables` may change. Source files, custom objects,
application builds, expressions, physics, mesh, boundary conditions, and solver settings are out
of scope.

## Isolation and acceptance

Protected gates use the pinned MOOSE HIT tool to enforce the exact input path and value, run
`--check-input`, execute the existing `combined-opt` application, reject the original unknown
identifier diagnostic, and preserve reference temperature, concentration, and diffusivity
quantities.

## Source and provenance

The mechanism is adapted from MOOSE Discussion 28157, where an unknown parsed-expression
identifier is traced to variable-coupling configuration. The benchmark fixture is an original
two-variable diffusion reduction reproduced on commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`; no discussion input was copied.

## Implementation checklist

- [x] Public contract, prompt, diagnosis, and failure evidence added
- [x] Private reference, gates, and required mutants added
- [x] Three faulty and three gold runs recorded
- [x] Gold and mutant scoring fixtures generated
- [x] Case enabled after discrimination passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/R2-COUPLED-VARIABLE-WIRING-001/case.yaml)
- [Prompt](../../benchmark/public/cases/R2-COUPLED-VARIABLE-WIRING-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)
