---
catalog_schema_version: "1.0"
case_id: INTEGRATED-EXAMPLE-001
title: Replace with a descriptive integrated workflow title
case_kind: integrated_workflow
track: null
subcategory: null
physics_domains:
  - replace_me
difficulty: L4
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
moose_validation_required: true
moose_validated: false
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - integrated
---

# Replace with the integrated workflow title

## End-to-end objective

Describe the complete participant objective without presenting the case as an atomic
capability measurement.

## Physical problem

Describe the governing problem, accepted model, and supplied starting state.

## Required workflow

List the ordered formulation, execution, diagnosis, repair, and verification work expected
from the participant.

## Expected deliverables

List required claims, final artifacts, execution outputs, and credibility evidence.

## Hard gates

Summarize the public gate categories without exposing evaluator-only thresholds.

## Stage-reached reporting

Explain how the first failed workflow stage will be reported.

## Failure attribution

Describe how participant, benchmark, and infrastructure failures are distinguished.

## Reference solution and credibility evidence

Summarize the accepted model and evidence provenance without copying private answers.

## Implementation checklist

- [ ] Public contract and prompt written
- [ ] Required artifacts added
- [ ] Private evaluator written
- [ ] Gold and mutant development submissions added
- [ ] Manifest entry added
- [ ] Bounded MOOSE validation and execution completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- Public case: `benchmark/public/cases/<case-id>/`
- Private evaluator: `benchmark/private/cases/<case-id>/`
- Manifest: `benchmark/manifest.yaml`

## Open questions and development notes

Record unresolved workflow, scientific, or implementation questions.
