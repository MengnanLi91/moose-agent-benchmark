# F2 Task — Weak Form and Boundary Terms

Read the supplied strong-form thermal problem and derive the finite-element residual for
temperature.

Return a structured claim with:

```json
{
  "residual_terms": [],
  "volume_terms": [],
  "natural_boundary_terms": [],
  "essential_boundary_handling": [],
  "test_function": "",
  "insulated_boundary": "",
  "residual_expression": ""
}
```

Identify the diffusion volume term, prescribed heat-flux contribution, convection
contribution, insulated-boundary treatment, prescribed-temperature treatment, integration
regions, and test function.

Use the outward-flux definition and residual convention supplied in the artifact. Do not use
MOOSE object names, write an input file, select a solver, or execute the problem.

Include evidence tied to `equation_specification` explaining how the supplied flux convention
determines the boundary-term signs.
