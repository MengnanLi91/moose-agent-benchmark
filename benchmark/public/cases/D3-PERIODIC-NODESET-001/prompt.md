# D3 Task — Localize the Periodic Pairing Failure

Inspect the immutable imported mesh, input, mesh report, warning, and pairing report. Identify:

- the root-cause family;
- the artifact in which the defect is localized;
- the two affected boundary names; and
- the specific boundary-entity mismatch.

Return these fields under `claim`:

```json
{
  "cause_family": "<stable identifier>",
  "artifact": "<stable identifier>",
  "boundaries": ["<name>", "<name>"],
  "defect": "<stable identifier>"
}
```

Include artifact-bound evidence from `mesh_report`, `periodic_warning`, and
`pairing_report`. Diagnose the current warning and failed pairing only. Do not infer or
report a historical fatal signature, edit the mesh, or run a repaired model.
