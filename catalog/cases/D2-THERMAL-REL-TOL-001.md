---
catalog_schema_version: "1.0"
case_id: D2-THERMAL-REL-TOL-001
title: Reconstruct Relative-Tolerance Nonconvergence
case_kind: atomic
track: DIAG
subcategory: D2
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: THERMAL-CONDUCTION-REL-TOL-BASE-001
status: in_progress
priority: normal
owner: MengnanLi91
reviewers: []
source_type: discussion_derived
source_name: DIAG Benchmark Discussion-Derived Case Plan
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - diag
  - d2
  - thermal
---

# Reconstruct Relative-Tolerance Nonconvergence

## Benchmark purpose

This atomic D2 case measures whether an agent reconstructs the ordered reason a nonlinear
solve fails its active convergence tests.

## Problem description

A small thermal solve ends with a residual below $10^{-6}$, but the relative tolerance is
a multiplier on the initial residual rather than an absolute target. The final residual
also remains above the configured absolute tolerance before the nonlinear iteration limit.

## What this case tests

**D2 — Causal-chain reconstruction.** The score covers causal ordering, the computed
relative target, and the terminal nonlinear outcome. Retuning tolerances is excluded.

## Starting information

The participant receives an immutable input, a residual report containing $R_0$, $R_f$,
`nl_rel_tol`, `nl_abs_tol`, solver reasons, and pinned run metadata.

## Required output

Return an ordered causal chain, the computed relative target, the terminal symptom, and an
artifact-bound observation.

## Permitted actions

- Inspect the supplied input and residual report.
- Compute $R_0\,\texttt{nl_rel_tol}$.

## Prohibited actions

- Modify or execute the input.
- Treat `nl_rel_tol` as an absolute threshold.

## Isolation rationale

The report supplies the measurements needed to reason about convergence without requiring
execution. Stable causal identifiers make ordering objective while leaving repair excluded.

## Evidence available to the participant

- `artifacts/failing.i`
- `evidence/residual-report.json`
- `evidence/run-metadata.json`

## Acceptance summary

The structured response must preserve the causal ordering and compute the active relative
target from the supplied values rather than compare $R_f$ directly with $10^{-6}$.

## Source and provenance

The case is derived from the DIAG benchmark discussion plan and constructed as a reduced
development fixture. It was reproduced three times on September 29, 2026 with
`combined-opt`, MOOSE commit `c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`,
and one process.

## Files

- [Public case contract](../../benchmark/public/cases/D2-THERMAL-REL-TOL-001/case.yaml)
- [Prompt](../../benchmark/public/cases/D2-THERMAL-REL-TOL-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)

## Implementation checklist

- [x] Public contract and prompt written
- [x] Required artifacts and evidence added
- [x] Private evaluator written
- [x] Gold and mutant development submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [x] Required MOOSE validation completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Open questions

Domain and benchmark-design review remain outstanding.

## Development notes

Keep evaluator identifiers, tolerances, private logs, and development answers out of the
generated public participant bundle.
