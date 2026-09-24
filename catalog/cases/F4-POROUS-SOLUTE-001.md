---
catalog_schema_version: "1.0"
case_id: F4-POROUS-SOLUTE-001
title: Assemble a MOOSE Input for 1-D Porous-Flow Tracer Transport
case_kind: atomic
track: FORM
subcategory: F4
physics_domains:
  - porous_media_and_species_transport
difficulty: L3
base_problem_id: MOOSE-POROUSFLOW-SOLUTE-BASE-001
status: in_progress
priority: high
owner: null
reviewers: []
source_type: moose_documentation
source_name: Flow and Solute Transport in Porous Media
source_url: https://github.com/idaholab/moose/tree/c2dfd9fedd3193740a5278ec32269450c618e3b7/modules/porous_flow/examples/solute_tracer_transport
domain_review_complete: false
benchmark_review_complete: false
moose_validation_required: true
moose_validated: true
github_issue: ""
github_pr: ""
tags:
  - benchmark-case
  - form
  - f4
  - porous-flow
  - tracer-transport
  - input-assembly
---

# Assemble a MOOSE Input for 1-D Porous-Flow Tracer Transport

## Benchmark purpose

This case evaluates **F4 — Input assembly and parameter wiring**. Physics, weak-form intent,
object plan, values, boundaries, execution controls, and outputs are supplied; the
participant must produce one runnable MOOSE input.

## Problem and scope

The variant models transient one-dimensional water and tracer transport through an 80 m
saturated porous medium. It requires two PorousFlow variables, six transport kernels,
constant porous properties, inlet pressure and tracer conditions, outlet pressure and tracer
outflow, midpoint concentration and Darcy-velocity outputs, and CSV reporting.

## Participant contract

The participant may inspect `artifacts/assembly-specification.md`, use one validation and one
execution attempt, and create `artifacts/solution.i`; the runner records it as the `moose_input` artifact. Changing supplied physics,
values, objects, or outputs is prohibited.

## Isolation and acceptance

The case isolates assembly and inter-object references. Official acceptance requires
successful input validation, bounded execution, final-time output generation, and semantic
preservation; execution alone cannot compensate for incorrect wiring.

## Source and provenance

The case is transformed from the MOOSE PorousFlow solute-tracer example. Syntax, reference
input, and QoIs were validated against MOOSE revision
`c2dfd9fedd3193740a5278ec32269450c618e3b7` on September 22, 2026.

## Implementation checklist

- [x] Public contract, prompt, assembly specification, and hashes added
- [x] Private evaluator, reference input, structure, and QoIs added
- [x] Gold and missing-dictator-variable mutant submissions added
- [x] Reference and gold pass `--check-input` and bounded execution
- [x] Mutant semantic and execution failures confirmed
- [x] Manifest entry added
- [x] Local repository validation passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

- [Public contract](../../benchmark/public/cases/F4-POROUS-SOLUTE-001/case.yaml)
- [Prompt](../../benchmark/public/cases/F4-POROUS-SOLUTE-001/prompt.md)
- [Assembly specification](../../benchmark/public/cases/F4-POROUS-SOLUTE-001/artifacts/assembly-specification.md)
