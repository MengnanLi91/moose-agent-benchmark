# F1 Task — Physics Specification and Constitutive Closure

Read the supplied engineering description and construct the physical model required to
predict the thermally induced bowing of the duct.

Return a structured claim containing:

```json
{
  "variables": [],
  "prescribed_fields": [],
  "governing_laws": [],
  "kinematics": [],
  "constitutive_relations": [],
  "closure_parameters": [],
  "boundary_conditions": [],
  "quantities_of_interest": []
}
```

Identify the solved primary variables, prescribed fields, governing balance law,
strain/kinematic description, elastic and thermal constitutive relations, closure
parameters, mechanical boundary conditions, and requested quantities of interest.

Use concise physics concepts rather than MOOSE object names. Do not derive the weak form,
select MOOSE objects, write an input file, choose solver parameters, or execute the problem.

Include at least one evidence record tied to `problem_specification` explaining which
supplied engineering facts support the formulation.
