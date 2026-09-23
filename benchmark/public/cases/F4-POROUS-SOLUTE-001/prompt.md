# F4 Task — Assemble a Runnable PorousFlow Input

Read the supplied assembly specification and create:

```text
artifacts/solution.i
```

The input must implement the supplied mesh, variables, PorousFlow configuration, materials,
kernels, boundary conditions, transient controls, midpoint postprocessors, and CSV output.

Return a submission claim with:

```json
{
  "assembled_input": true,
  "variables": ["porepressure", "C"],
  "mesh": {},
  "porous_flow": {},
  "properties": {},
  "boundary_conditions": [],
  "required_outputs": ["C_midpoint", "Darcy_velocity_midpoint"],
  "execution": {}
}
```

Attach exactly one artifact with role `moose_input`. Include evidence tied to
`assembly_specification` explaining how the submitted input preserves the supplied model.

Do not change the supplied physics, values, object plan, reporting location, or execution
controls.
