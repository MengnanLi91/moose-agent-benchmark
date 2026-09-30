---
catalog_schema_version: "1.0"
case_id: D3-PERIODIC-NODESET-001
title: Localize Periodic Pairing Failure to Nodeset Boundaries
case_kind: atomic
track: DIAG
subcategory: D3
physics_domains:
  - thermal_energy_transport
difficulty: L2
base_problem_id: PERIODIC-IMPORTED-MESH-BASE-001
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
  - d3
  - periodic
---

# Localize Periodic Pairing Failure to Nodeset Boundaries

## Benchmark purpose

This atomic D3 case measures whether an agent localizes a failed periodic pairing to the
boundary entity types stored in an imported mesh.

## Problem description

The requested `left_nodes` and `right_nodes` names exist only as node sets. MOOSE emits its
current boundary-match warning and completes the simple solve without establishing the
requested x-periodic constraints.

## What this case tests

**D3 — Root-cause localization.** The score covers the cause family, faulty artifact,
affected boundary names, and entity-type defect. Mesh repair is excluded.

## Starting information

The participant receives the immutable imported mesh and input, a boundary metadata report,
the current warning, the failed pairing result, and pinned run metadata.

## Required output

Return the cause family, localized artifact, two boundary names, precise entity mismatch,
and artifact-bound evidence.

## Permitted actions

- Inspect the supplied mesh, input, and reports.
- Localize the mismatch to the imported artifact.

## Prohibited actions

- Edit or execute the mesh and input.
- Infer the unreproduced historical fatal error.

## Isolation rationale

The public evidence establishes both mesh metadata and pairing outcome. A private sideset
control confirms localization without exposing the repaired artifact to participants.

## Evidence available to the participant

- `artifacts/failing.i`
- `artifacts/periodic_mesh.e`
- `evidence/mesh-report.txt`
- `evidence/periodic-warning.log`
- `evidence/pairing-report.json`
- `evidence/run-metadata.json`

## Acceptance summary

The structured response must localize the current failed pairing to boundary entity types
in the imported mesh. The historical fatal signature is intentionally absent.

## Source and provenance

The case is derived from the DIAG benchmark discussion plan and constructed from a generated
mesh imported through Exodus. On September 29, 2026, three faulty/control pairs reproduced
the warning and pairing difference with `combined-opt`, MOOSE commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`, and one process.

## Files

- [Public case contract](../../benchmark/public/cases/D3-PERIODIC-NODESET-001/case.yaml)
- [Prompt](../../benchmark/public/cases/D3-PERIODIC-NODESET-001/prompt.md)
- [Manifest](../../benchmark/manifest.yaml)

## Implementation checklist

- [x] Public contract and prompt written
- [x] Required artifacts and evidence added
- [x] Private evaluator and sideset control written
- [x] Gold and mutant development submissions added
- [x] Manifest entry added
- [x] Local validation passes
- [x] Required MOOSE validation completed
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Open questions

Domain and benchmark-design review remain outstanding.

## Development notes

Keep the private sideset control, evaluator, validation outputs, and development answers out
of the generated public participant bundle.
