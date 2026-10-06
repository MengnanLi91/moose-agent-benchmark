# R2 Task — Repair a Missing Coupled-Variable Declaration

Read the immutable failing input and supplied diagnosis. Create:

- `response.json`
- `artifacts/solution.i`

`solution.i` must be a complete replacement for `failing.i`. The parsed material expression
depends on an existing nonlinear temperature variable, but that dependency is not declared.
Repair only the variable-coupling declaration on the existing
`Materials/dependent_diffusivity` object.

Use these stable response values:

```json
{
  "claim": {
    "repair_class": "coupled_variable_wiring",
    "changed_paths": ["artifacts/solution.i"],
    "changed_regions": ["material_variable_coupling"],
    "expected_failure_removed": "missing_coupled_variable"
  },
  "evidence": [
    {
      "source_id": "failure_evidence",
      "observation": "missing_variable_coupling: <artifact-bound observation>",
      "interpretation": "<why the declared dependency is required>"
    },
    {
      "source_id": "repaired_moose_input",
      "observation": "declared_variable_dependency: <submitted change>",
      "interpretation": "<why this is the minimal repair>"
    }
  ]
}
```

Do not change the material expression, object types, variables, kernels, coefficients, mesh,
boundary conditions, solver configuration, tolerances, outputs, or postprocessors. Do not
replace the temperature dependency with a constant or function workaround.
