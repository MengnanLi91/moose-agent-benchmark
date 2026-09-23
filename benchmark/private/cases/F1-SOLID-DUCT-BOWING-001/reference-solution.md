# Reference solution

Case: `F1-SOLID-DUCT-BOWING-001`

## Required answer

The response must provide the following claim values. Additional explanatory fields are
allowed, but they do not add credit.

```json
{
  "variables": [
    "displacement_x",
    "displacement_y",
    "displacement_z"
  ],
  "prescribed_fields": ["temperature"],
  "governing_laws": [
    "quasi_static_balance_of_linear_momentum"
  ],
  "kinematics": ["finite_strain"],
  "constitutive_relations": [
    "isotropic_linear_elasticity",
    "thermal_expansion_eigenstrain"
  ],
  "closure_parameters": [
    "youngs_modulus",
    "poissons_ratio",
    "thermal_expansion_coefficient",
    "stress_free_temperature"
  ],
  "boundary_conditions": [
    "fixed_bottom_displacement_x",
    "fixed_bottom_displacement_y",
    "fixed_bottom_displacement_z",
    "traction_free_remaining_surfaces",
    "prescribed_spatial_temperature_field"
  ],
  "quantities_of_interest": [
    "lateral_centerline_displacement_core_top",
    "lateral_centerline_displacement_aclp",
    "lateral_centerline_displacement_duct_top"
  ]
}
```

The evidence record must use `source_id = problem_specification`. A full-credit example is:

```json
{
  "source_id": "problem_specification",
  "observation": "The fixed duct has an imposed axial and cross-sectional temperature gradient.",
  "interpretation": "Displacement is solved while prescribed temperature produces deformation through thermal expansion."
}
```

## Governing equations

The solved field is the displacement vector

$$
\mathbf{u}=(u_x,u_y,u_z).
$$

Temperature $T(\mathbf{x})$ is prescribed and is not solved. Under quasi-static conditions,
with no body force, linear momentum balance is

$$
\nabla\cdot\boldsymbol{\sigma}=0.
$$

The designated reference kinematics are finite strain. The conceptual strain decomposition
is

$$
\boldsymbol{\epsilon}
=
\boldsymbol{\epsilon}^{e}
+
\boldsymbol{\epsilon}^{th}.
$$

The isotropic elastic response and thermal eigenstrain are

$$
\boldsymbol{\sigma}
=
\mathbb{C}(E,\nu):\boldsymbol{\epsilon}^{e},
$$

$$
\boldsymbol{\epsilon}^{th}
=
\alpha\left(T-T_{\mathrm{sf}}\right)\mathbf{I}.
$$

The closure values are $E=1.7\times10^{11}\ \mathrm{Pa}$, $\nu=0.30$,
$\alpha=18.0\times10^{-6}\ \mathrm{K}^{-1}$, and
$T_{\mathrm{sf}}=400^\circ\mathrm{C}$.

## Boundary conditions and quantities of interest

At the bottom surface,

$$
u_x=0,\qquad u_y=0,\qquad u_z=0.
$$

All remaining surfaces are traction free. The prescribed temperature field creates
differential thermal expansion, so the hotter side expands more and the duct bows toward
the colder side.

The requested outputs are lateral centerline displacement at $z=2.5\ \mathrm{m}$,
$z=3.0\ \mathrm{m}$, and $z=4.0\ \mathrm{m}$.

## Weak formulation

A weak-form derivation is not required and is not graded in this F1 case.

## MOOSE representation

MOOSE object selection, input syntax, solver configuration, execution, and numerical
displacement values are outside the required answer and receive no credit.

# Grading rubric

## Scoring model

The evaluator computes three component scores:

- capability: 70% of the raw score;
- evidence: 20% of the raw score;
- submission contract: 10% of the raw score.

Thus,

```text
raw_score = 0.70 * capability + 0.20 * evidence + 0.10 * contract
```

The capability and evidence points below are points within their respective 100-point
components. The case passes only if all gates pass, capability is at least 80, and the raw
score is at least 80. Any failed gate makes the official score zero.

Set-valued criteria use set F1: omitted expected items reduce recall, and extra items reduce
precision. The two constitutive-relation criteria are exact membership checks.

## C1: Solved and prescribed fields — 20 capability points

Full credit:
The three displacement components are solved variables, and temperature is prescribed.
Each half is worth 10 points.

Partial credit:
Set F1 gives proportional credit for incomplete lists, with penalties for extra items.

No credit:
The response solves temperature instead of displacement or omits both fields.

Common errors:
Listing temperature as a fourth nonlinear variable.

## C2: Governing law and kinematics — 20 capability points

Full credit:
The response identifies quasi-static balance of linear momentum and finite strain.
Each item is worth 10 points.

Partial credit:
One correct item earns its 10-point subcriterion; set F1 applies within each list.

No credit:
The response uses an unrelated balance law and does not identify finite strain.

Acceptable alternatives:
Equivalent equations may appear in explanatory text, but the structured claim must use the
canonical identifiers shown above.

## C3: Constitutive model and closure — 40 capability points

Full credit:
The response includes isotropic linear elasticity (10 points), thermal-expansion eigenstrain
(20 points), and all four closure parameters (10 points).

Partial credit:
The elasticity and eigenstrain checks are each all-or-nothing. The closure-parameter list
uses set F1 and therefore permits proportional credit.

No credit:
The response provides no elastic law, no thermal coupling, and no closure parameters.

Common errors:
Omitting `thermal_expansion_eigenstrain`, the thermal expansion coefficient, or the
stress-free temperature.

## C4: Boundary conditions — 10 capability points

Full credit:
All three bottom displacement constraints, traction-free remaining surfaces, and the
prescribed spatial temperature field are listed.

Partial credit:
Set F1 gives proportional credit for correct members of an incomplete or overinclusive list.

No credit:
The listed conditions do not describe the supplied support and thermal loading.

## C5: Quantities of interest — 10 capability points

Full credit:
All three lateral centerline displacements are identified: core top, above-core load-pad
elevation, and duct top.

Partial credit:
Set F1 gives proportional credit when only some locations are included.

No credit:
None of the requested displacement quantities is identified.

## E1: Evidence source — 40 evidence points

Full credit:
The first evidence record uses `source_id = problem_specification`.

No credit:
The source identifier is missing or different.

## E2: Observation — 30 evidence points

Full credit:
The observation contains the phrase `temperature gradient`.

No credit:
The observation does not identify the imposed temperature gradient.

## E3: Interpretation — 30 evidence points

Full credit:
The interpretation contains the phrase `thermal expansion`.

No credit:
The interpretation does not connect temperature to deformation through thermal expansion.

## Submission contract — 100 contract points

The contract component is:

- 40 points after the submission schema and case identity validate;
- 30 points for the fraction of the eight required claim paths that are present;
- 15 points for valid evidence source references and hashes; and
- 15 points for satisfying the no-artifact contract.

Invalid submission identity is rejected before scoring. Evidence and artifact contract
checks are all-or-nothing within their 15-point allocations.

## Gates

The submission must include no artifacts and must remain within the declared time, CPU, and
attempt budgets. Failure of either automatic gate sets the official case score to zero.
