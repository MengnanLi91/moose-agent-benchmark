# Reference solution

Case: `F1-SOLID-DUCT-BOWING-001`

## Required answer

A full-credit response naturally states the solved and prescribed fields, momentum balance, finite-strain kinematics, isotropic elasticity, thermal eigenstrain closure, mechanical boundary conditions, and all requested displacement quantities. No prescribed JSON keys or evidence identifiers are required.

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

# Semantic grading

The private rubric grades the physical formulation directly. Equivalent prose, equations, variable names, and organization are accepted. Submission integrity and runner metadata are validation checks, not FORM score components.
