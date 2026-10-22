---
catalog_schema_version: "1.0"
case_id: V1-THERMOELASTIC-MMS-001
title: "Plane-Strain Thermoelastic MMS"
case_kind: atomic
track: VERIFY
subcategory: V1
mms_task: derivation
physics_domains:
  - thermal_energy_transport
  - solid_mechanics
difficulty: L4
base_problem_id: THERMOELASTIC-MMS-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: synthetic
source_name: "Deriving an MMS Benchmark from the MOOSEnger Verification Runs"
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags: [benchmark-case, verify, v1, mms]
---

# Plane-Strain Thermoelastic MMS

## Benchmark purpose

Evaluate derivation of coupled thermal and mechanical source terms, plane-strain stresses, and
boundary data for a thermoelastic manufactured solution.

## Capability boundary

MOOSE construction and execution are excluded. The participant derives sources, boundary and initial data, and applicable compatibility or constitutive conditions.

## Required output

Submit `response.md` containing the requested derivation and enough intermediate work to audit signs and coefficients.

## Implementation status

The public contract, private evaluator, development fixtures, and manifest registration are complete. The case remains disabled until live derivation-judge calibration and domain and benchmark-design reviews are complete.

## Review checklist

- [ ] Exact solution and forcing independently re-derived
- [x] Gold response accepted and mutant rejected
- [ ] Live derivation-judge calibration complete
- [ ] Domain review complete
- [ ] Benchmark-design review complete
