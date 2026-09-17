---
catalog_schema_version: "1.0"
case_id: DIAG-THERMAL-SCHEMA-001
title: Classify an unregistered MOOSE object failure
case_kind: atomic
track: DIAG
subcategory: D1
physics_domains:
  - thermal_energy_transport
difficulty: L1
base_problem_id: THERMAL-CONDUCTION-BASE-001
status: in_progress
priority: normal
owner: MengnanLi91
reviewers: []
source_type: synthetic
source_name: MOOSE check-input fixture
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - diag
  - d1
  - thermal
---

# Classify an unregistered MOOSE object failure

## Benchmark purpose

This case measures whether an agent can classify the earliest failing MOOSE workflow stage
from an immutable input and its supplied `--check-input` log.

## Problem description

The intended model is steady scalar diffusion on a one-dimensional generated mesh. The
physical formulation and boundary conditions are supplied as correct. MOOSE stops while
validating the requested object type, before problem execution or nonlinear solution.

## What this case tests

**D1 — Failure-stage classification.** Full credit depends on separating the earliest
object-schema validation failure from the terminal input-validation symptom. The case does
not score object replacement, input repair, or solver configuration.

## Starting information

The participant receives the immutable failing input, a captured MOOSE validation log, and
the statement that the physical equation and boundary conditions are correct.

## Required output

Return the earliest failing workflow stage, the terminal symptom, and one artifact-bound
observation with an interpretation supporting the classification.

## Permitted actions

- Inspect the supplied input.
- Inspect the supplied check-input log.

## Prohibited actions

- Modify or execute the input.
- Consult evaluator-only files.

## Isolation rationale

The supplied physical formulation prevents formulation work from dominating the result.
Repair is explicitly excluded, and the immutable artifact prevents successful modification
from substituting for diagnosis.

## Case construction

This synthetic case starts from a minimal scalar-diffusion input and introduces one
unregistered object-type defect. The public log records the resulting validation failure.

## Evidence available to the participant

- `artifacts/failing.i`
- `evidence/check_input.log`

## Acceptance summary

The response must classify the failure at the correct pre-execution stage and bind that
classification to the supplied log. Exact evaluator values and weights remain outside this
catalog record.

## Source and provenance

The case is a synthetic development fixture for the benchmark harness. It targets
`moose_test-opt` using the version identifier recorded in the public case contract.

## Implementation checklist

- [x] Public contract written
- [x] Prompt and supplied artifacts added
- [x] Private evaluator written
- [x] Gold and mutant development submissions added
- [x] Manifest entry added
- [x] Automated tests pass
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public case contract](../../benchmark/public/cases/DIAG-THERMAL-SCHEMA-001/case.yaml)
- [Prompt](../../benchmark/public/cases/DIAG-THERMAL-SCHEMA-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)

## Open questions

None currently recorded.

## Development notes

Do not add the private expected classification, evaluator weights, or hidden diagnostics to
this public-facing record.
