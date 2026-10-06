# R3 Task — Repair an Incomplete Nested Field-Split Partition

Read the immutable failing input and supplied diagnosis. Create:

- `response.json`
- `artifacts/solution.i`

Preserve the hierarchy `fluid + concentration`, then `velocity + pressure`. Change only variable
ownership and mechanically necessary split wiring under `[Preconditioning]`. Do not replace the
field split, alter PETSc leaf solvers, drop or overlap variables, or change physics or tolerances.

Use these stable response values:

```json
{
  "claim": {
    "repair_class": "fieldsplit_variable_partition",
    "changed_paths": ["artifacts/solution.i"],
    "changed_regions": ["preconditioning_fieldsplit_ownership"],
    "expected_failure_removed": "fieldsplit_parent_child_size_mismatch"
  },
  "evidence": [
    {
      "source_id": "failure_evidence",
      "observation": "incomplete_parent_split: <artifact-bound observation>",
      "interpretation": "<why ownership must be explicit>"
    },
    {
      "source_id": "repaired_moose_input",
      "observation": "complete_nonoverlapping_partition: <submitted change>",
      "interpretation": "<why the hierarchy is preserved>"
    }
  ]
}
```
