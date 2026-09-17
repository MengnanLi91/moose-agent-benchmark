---
catalog_schema_version: "1.0"
case_id: FORM-EXAMPLE-F1-001
title: Replace with a descriptive case title
case_kind: atomic
track: FORM
subcategory: F1
physics_domains:
  - replace_me
difficulty: L1
base_problem_id: REPLACE-ME-BASE-001
status: planned
priority: normal
owner: null
reviewers: []
source_type: synthetic
source_name: ""
source_url: ""
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: false
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
---

# Replace with the case title

## Benchmark purpose

Explain why the case exists and what successful behavior demonstrates.

## Problem description

Describe the physical or numerical problem for a domain expert.

## What this case tests

Name the single primary atomic subcategory, the graded behavior, and nearby capabilities
that are intentionally excluded.

## Starting information

Summarize the upstream truth, artifacts, and evidence supplied to the participant.

## Required output

Describe the required claims and artifact roles in terms consistent with `case.yaml`.

## Permitted actions

- Replace with allowed inspection, validation, execution, or editing actions.

## Prohibited actions

- Replace with actions that would violate the capability boundary.

## Isolation rationale

Explain why upstream differences cannot dominate, why downstream work is unnecessary, and
how the case avoids scoring more than one primary capability.

## Case construction

Describe the accepted base problem, transformation, or injected mutation. Do not disclose
private answers or thresholds.

## Evidence available to the participant

- List participant-visible evidence.

## Acceptance summary

Summarize acceptance at a public level without copying evaluator-only criteria.

## Source and provenance

Record the original source, version, target application, MOOSE revision, license, and
redistribution notes.

## Implementation checklist

- [ ] Public contract and prompt written
- [ ] Required artifacts and evidence added
- [ ] Private evaluator written
- [ ] Gold and mutant development submissions added
- [ ] Manifest entry added
- [ ] Local validation passes
- [ ] Required MOOSE validation completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- Public case: `benchmark/public/cases/<case-id>/`
- Private evaluator: `benchmark/private/cases/<case-id>/`
- Development fixtures: `benchmark/example-submissions/`
- Manifest: `benchmark/manifest.yaml`

## Open questions

Record unresolved benchmark-design or scientific questions.

## Development notes

Record implementation details useful to future maintainers.
