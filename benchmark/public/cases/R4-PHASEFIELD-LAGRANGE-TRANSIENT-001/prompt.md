# R4 Task — Recover a Transient Lagrange-Constraint Solver Breakdown

Read the immutable failing input and supplied diagnosis. Create:

- `response.json`
- `artifacts/solution.i`

Change exactly two values: the multiplier variable's initial value and the Lagrange constraint's
`epsilon`. Both must be small and nonzero. Do not alter the timestep, solver, tolerances, phase
initial fields, free energies, kernels, mesh, or constraint target.

Use these stable response values:

```json
{
  "claim": {
    "repair_class": "lagrange_transient_regularization",
    "changed_paths": ["artifacts/solution.i"],
    "changed_regions": ["lambda_initial_condition", "constraint_regularization"],
    "expected_failure_removed": "lagrange_transient_subpc_failure"
  },
  "evidence": [
    {
      "source_id": "failure_evidence",
      "observation": "transient_zero_regularization_breakdown: <artifact-bound observation>",
      "interpretation": "<why the zero/zero state breaks down after progress>"
    },
    {
      "source_id": "repaired_moose_input",
      "observation": "nonzero_multiplier_and_regularization: <submitted change>",
      "interpretation": "<why this is the minimal transient repair>"
    }
  ]
}
```

The accepted numeric ranges and tolerances are private and are not exact-match requirements.
