---
catalog_schema_version: "1.0"
case_id: F2-THERMAL-REFLECTOR-001
title: Steady Heat Conduction in a PB-FHR Reflector Block
case_kind: atomic
track: FORM
subcategory: F2
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: VTB-PBFHR-REFLECTOR-CONDUCTION-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: vtb
source_name: PB-FHR Bypass Flow Reflector Model
source_url: https://github.com/idaholab/virtual_test_bed/tree/1c7337a264d44ee4cdc64c0855e156be2f3b8ce6/pbfhr/mark1/reflector
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - form
  - f2
  - heat-conduction
  - weak-form
  - vtb
---

# Steady Heat Conduction in a PB-FHR Reflector Block

## Benchmark purpose

This case evaluates **F2 — Weak form and boundary terms**. The participant receives a
complete steady heat-conduction strong form and derives the finite-element residual.

## Problem and scope

The reduced graphite-reflector problem has constant conductivity, inward prescribed heat
flux, barrel convection, a prescribed-temperature interface, and insulated remaining
surfaces. The score covers integration by parts, test functions, integration regions,
essential versus natural conditions, and boundary signs.

MOOSE object selection, input construction, solver choices, execution, and numerical
verification are excluded.

## Participant contract

The participant may inspect `artifacts/equation-specification.md` and return a natural Markdown weak-form derivation. Equivalent notation, term ordering, and consistent sign conventions are accepted. No MOOSE object names are permitted.

## Isolation and acceptance

All physics and boundary data are supplied, so formulation choices cannot substitute for the
target weak-form derivation. Full credit requires the diffusion volume term, correct
prescribed-flux and convection signs, zero insulated contribution, and essential treatment
of prescribed temperature.

## Source and provenance

The case is reduced from the VTB PB-FHR reflector solid-conduction model at revision
`1c7337a264d44ee4cdc64c0855e156be2f3b8ce6`, verified September 22, 2026.

## Implementation checklist

- [x] Public contract, prompt, and strong-form artifact added
- [x] Private evaluator and reference solution added
- [x] Gold and sign-mutant submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/F2-THERMAL-REFLECTOR-001/case.yaml)
- [Prompt](../../benchmark/public/cases/F2-THERMAL-REFLECTOR-001/prompt.md)
- [Equation specification](../../benchmark/public/cases/F2-THERMAL-REFLECTOR-001/artifacts/equation-specification.md)
