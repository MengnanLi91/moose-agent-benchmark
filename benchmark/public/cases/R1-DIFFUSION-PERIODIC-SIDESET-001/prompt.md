# R1 Task — Repair a Partially Overlapping Periodic Sideset

Read the immutable failing input and supplied diagnosis. Create:

- `response.json`
- `artifacts/solution.i`

Only create or restrict the right periodic sideset and update its periodic reference. Do not alter
the translation, topology, equation, nonperiodic boundary condition, solver, or outputs.

Use this response shape and the stable identifiers exactly:

```json
{
  "claim": {
    "repair_class": "periodic_sideset_restriction",
    "changed_paths": ["artifacts/solution.i"],
    "changed_regions": ["mesh_periodic_sideset", "periodic_boundary_reference"],
    "expected_failure_removed": "periodic_neighbor_lookup_failure"
  },
  "evidence": [
    {
      "source_id": "failure_evidence",
      "observation": "unmatched_periodic_sideset: <artifact-bound observation>",
      "interpretation": "<why the supplied diagnosis requires a restricted sideset>"
    },
    {
      "source_id": "repaired_moose_input",
      "observation": "restricted_periodic_sideset: <submitted change>",
      "interpretation": "<why this is the minimal repair>"
    }
  ]
}
```

Do not claim protected gate results. The evaluator reruns the captured artifact in a clean fixture.
