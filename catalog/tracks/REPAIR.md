# REPAIR — Repair and execution recovery

REPAIR evaluates bounded changes that restore a supplied failing MOOSE model.

## Subcategories

- [[../subcategories/R1|R1 — HIT, schema, and reference repair]]
- [[../subcategories/R2|R2 — Residual, Jacobian, and coupling repair]]
- [[../subcategories/R3|R3 — Solver, scaling, and nullspace repair]]
- [[../subcategories/R4|R4 — Initialization and step-control repair]]

Atomic REPAIR cases should supply the relevant diagnosis and contain one independent primary
defect. Unrelated model changes must not receive credit.

## Cases

Open the `REPAIR` view in [[../benchmark.base|Benchmark Cases]].
