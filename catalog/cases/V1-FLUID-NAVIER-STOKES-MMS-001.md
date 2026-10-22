---
catalog_schema_version: "1.0"
case_id: V1-FLUID-NAVIER-STOKES-MMS-001
title: "Incompressible Navier-Stokes MMS"
case_kind: atomic
track: VERIFY
subcategory: V1
mms_task: implementation
physics_domains:
  - fluid_dynamics
difficulty: L4
base_problem_id: NAVIER-STOKES-MMS-BASE-001
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

# Incompressible Navier-Stokes MMS

## Benchmark purpose

Verify third-order velocity and second-order pressure convergence for the Taylor-Hood
discretization. The participant receives the complete MMS equations and protected
instrumentation, then authors and verifies a MOOSE input. The cell-average divergence output
is retained as an unscored diagnostic.

## Capability boundary

MMS derivation and the refinement sequence are supplied. Input construction, successful execution, and demonstrated convergence are scored.

## Required output

Submit `artifacts/solution.i` and `response.json` containing the authoritative four-level convergence report.

## Implementation status

The public contract, private evaluator, development fixtures, manifest registration, and pinned real-MOOSE calibration are complete. The case remains disabled until domain and benchmark-design reviews are complete.

## Review checklist

- [ ] Exact solution and forcing independently re-derived
- [x] Canonical input passes `--check-input`
- [x] All four authoritative runs complete
- [x] Final two orders meet the formal-order band
- [x] Gold response accepted and mutant rejected
- [ ] Domain review complete
- [ ] Benchmark-design review complete
