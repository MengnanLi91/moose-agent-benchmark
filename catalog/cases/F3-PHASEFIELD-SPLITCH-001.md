---
catalog_schema_version: "1.0"
case_id: F3-PHASEFIELD-SPLITCH-001
title: Map a Split Cahn-Hilliard Formulation to MOOSE Objects
case_kind: atomic
track: FORM
subcategory: F3
physics_domains:
  - phase_transformation_and_microstructure
difficulty: L3
base_problem_id: MOOSE-PHASEFIELD-SPLITCH-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: moose_documentation
source_name: Split Cahn-Hilliard Phase Field implementation
source_url: https://github.com/idaholab/moose/tree/c2dfd9fedd3193740a5278ec32269450c618e3b7/modules/phase_field
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - form
  - f3
  - phase-field
  - cahn-hilliard
  - object-map
---

# Map a Split Cahn-Hilliard Formulation to MOOSE Objects

## Benchmark purpose

This case evaluates **F3 — MOOSE object and coupling map**. The mathematical split
Cahn-Hilliard formulation is supplied; the participant maps each term to the permitted
MOOSE-native decomposition.

## Problem and scope

The supplied system uses concentration and chemical-potential variables, constant mobility
and gradient energy, a derivative-dependent free energy, and natural zero-flux boundaries.
The score covers residual ownership, coupled-variable parameters, material-property names,
and cross-variable completeness.

Physics selection, weak-form derivation, complete input syntax, solvers, and execution are
excluded.

## Participant contract

The participant may inspect `artifacts/weak-form-specification.md` and return the object/material/coupling map as prose, a table, or a list using only the supplied registry.

## Isolation and acceptance

Because the weak form and allowed registry are fixed, the case isolates MOOSE representation
knowledge. Full credit requires assigning the coupled concentration time derivative to the
chemical-potential residual and using a derivative-capable free-energy material.

## Source and provenance

Object behavior and parameter names are pinned to MOOSE revision
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, verified September 22, 2026.

## Implementation checklist

- [x] Public contract, prompt, weak form, and registry added
- [x] Private evaluator and reference map added
- [x] Gold and coupled-time-derivative mutant submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/F3-PHASEFIELD-SPLITCH-001/case.yaml)
- [Prompt](../../benchmark/public/cases/F3-PHASEFIELD-SPLITCH-001/prompt.md)
- [Weak-form specification](../../benchmark/public/cases/F3-PHASEFIELD-SPLITCH-001/artifacts/weak-form-specification.md)
