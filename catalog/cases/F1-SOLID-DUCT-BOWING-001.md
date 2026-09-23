---
catalog_schema_version: "1.0"
case_id: F1-SOLID-DUCT-BOWING-001
title: Thermally Induced Bowing of a Hexagonal Reactor Duct
case_kind: atomic
track: FORM
subcategory: F1
physics_domains:
  - solid_and_structural_mechanics
  - coupled_engineering_systems
difficulty: L3
base_problem_id: VTB-IAEA-VP1-DUCT-BOWING-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: vtb
source_name: Hexagonal Duct Bowing - Linear Thermal Gradient (IAEA VP1)
source_url: https://virtualtestbed.inl.gov/sfr/hex_duct_bowing/hex_duct_linear.html
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - form
  - f1
  - solid-mechanics
  - thermo-mechanics
  - duct-bowing
  - vtb
---

# Thermally Induced Bowing of a Hexagonal Reactor Duct

## Benchmark purpose

This atomic case evaluates **F1 — Physics specification and constitutive closure**. The
participant receives a complete engineering description of a thermally loaded hexagonal
reactor duct and identifies the physical model required for free thermo-mechanical
deformation.

## Problem and scope

A prescribed axial and cross-sectional temperature gradient causes differential thermal
expansion and lateral duct bowing. The score covers displacement unknowns, prescribed
temperature, quasi-static momentum balance, finite-strain kinematics, isotropic elasticity,
thermal eigenstrain, closure parameters, mechanical boundaries, and requested displacement
quantities.

Weak-form derivation, MOOSE object selection, input construction, solver configuration,
execution, and numerical verification are excluded.

## Participant contract

The participant may inspect `artifacts/engineering-description.md` and return only a
structured physics specification with artifact-grounded evidence. MOOSE object names and
input files are prohibited.

## Isolation and acceptance

Geometry, material data, temperature, support conditions, and reporting locations are
supplied. Full credit requires recognizing displacement as the solved field, temperature as
prescribed, and thermal expansion eigenstrain as the coupling from temperature to stress.

## Source and provenance

The case is based on the VTB IAEA VP1 hexagonal duct-bowing model. The engineering source is
pinned to VTB revision `1c7337a264d44ee4cdc64c0855e156be2f3b8ce6`, and MOOSE terminology
is pinned to revision `c2dfd9fedd3193740a5278ec32269450c618e3b7`, verified September 22,
2026.

## Implementation checklist

- [x] Public contract, prompt, and engineering description added
- [x] Private evaluator and reference solution added
- [x] Gold and missing-thermal-expansion mutant submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/F1-SOLID-DUCT-BOWING-001/case.yaml)
- [Prompt](../../benchmark/public/cases/F1-SOLID-DUCT-BOWING-001/prompt.md)
- [Engineering description](../../benchmark/public/cases/F1-SOLID-DUCT-BOWING-001/artifacts/engineering-description.md)
