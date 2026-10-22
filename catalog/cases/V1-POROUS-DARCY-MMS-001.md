---
catalog_schema_version: "1.0"
case_id: V1-POROUS-DARCY-MMS-001
title: "Variable-Permeability PorousFlow Darcy MMS"
case_kind: atomic
track: VERIFY
subcategory: V1
mms_task: implementation
physics_domains:
  - porous_media_flow
difficulty: L3
base_problem_id: DARCY-VARIABLE-K-BASE-001
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

# Variable-Permeability PorousFlow Darcy MMS

## Benchmark purpose

Verify second-order pressure convergence with variable permeability using PorousFlow objects. The participant receives complete MMS equations and protected instrumentation, then authors and verifies a MOOSE input.

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
