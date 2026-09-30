---
catalog_schema_version: "1.0"
case_id: D1-SOLVER-DTMIN-001
title: Distinguish Linear Solve Failure from dtmin Termination
case_kind: atomic
track: DIAG
subcategory: D1
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: TRANSIENT-DIFFUSION-DTMIN-BASE-001
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
  - d1
  - solver
---

# Distinguish Linear Solve Failure from dtmin Termination

## Benchmark purpose

This atomic D1 case measures whether an agent separates the earliest failed solver stage
from the downstream message that terminates a transient run.

## Problem description

A small transient diffusion problem has a deterministic zero-iteration linear limit. The
captured event sequence shows linear divergence at `dt=2`, nonlinear propagation, cutback
to `dt=1`, repeated failure, and final termination at the minimum timestep.

## What this case tests

**D1 — Failure-stage classification.** Only the first failed stage and the distinct terminal
symptom are graded. Root-cause repair and solver configuration are outside the score.

## Starting information

The participant receives an immutable input, ordered solver events, and pinned run metadata.

## Required output

Return the earliest failure-stage identifier, the terminal-symptom identifier, and separate
artifact-bound evidence for each.

## Permitted actions

- Inspect the supplied input and evidence.
- Classify the ordered failure sequence.

## Prohibited actions

- Modify or execute the input.
- Repair the solver setup or time stepper.

## Isolation rationale

The final `dtmin` message is deliberately downstream of the first solver failure. Requiring
two evidence entries prevents the terminal symptom from substituting for stage classification.

## Evidence available to the participant

- `artifacts/failing.i`
- `evidence/solver-events.json`
- `evidence/run-metadata.json`

## Acceptance summary

The structured response must distinguish the first failed stage from the propagated
minimum-timestep termination and bind each statement to the ordered event evidence.

## Source and provenance

The case is derived from the DIAG benchmark discussion plan and constructed as a reduced
development fixture. It was reproduced three times on September 29, 2026 with
`combined-opt`, MOOSE commit `c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`,
and one process.

## Files

- [Public case contract](../../benchmark/public/cases/D1-SOLVER-DTMIN-001/case.yaml)
- [Prompt](../../benchmark/public/cases/D1-SOLVER-DTMIN-001/prompt.md)
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

Keep evaluator weights, gold identifiers, private logs, and reproduction details out of the
generated public participant bundle.
