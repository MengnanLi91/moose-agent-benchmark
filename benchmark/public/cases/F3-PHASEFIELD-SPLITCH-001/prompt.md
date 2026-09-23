# F3 Task — MOOSE Object and Coupling Map

Read the supplied split Cahn-Hilliard weak formulation and permitted object registry.

Return:

```json
{
  "variables": {},
  "residual_object_map": [],
  "materials": [],
  "couplings": []
}
```

For every supplied residual term, identify the MOOSE object, residual variable, coupled
variables, material properties, and relevant parameter names. Also identify the
derivative-capable free-energy material and constant-property material wiring.

List residual mappings in this order: concentration time derivative, chemical-potential
gradient, then concentration/free-energy relation.

Do not rederive Cahn-Hilliard, add unlisted object types, or write a complete `.i` file.

Include evidence tied to `weak_form_specification` explaining how at least one supplied weak
term determines its MOOSE object and coupling.
