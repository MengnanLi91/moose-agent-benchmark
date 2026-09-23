# Engineering Problem Specification

## Geometry

Consider a thin-walled hexagonal reactor duct with:

- corner-to-corner distance: 150 mm;
- wall thickness: 3 mm;
- total axial length: 4000 mm;
- active core region: $z=1500$ mm to $z=2500$ mm; and
- above-core load-pad reporting elevation: $z=3000$ mm.

## Thermal loading

Temperature is prescribed throughout the duct and is not a solved variable.

Below the active core region, the temperature is uniformly $400^\circ\mathrm{C}$. Within
the active core, temperature increases linearly with axial position. At the core top, the
hot-side corner is $550^\circ\mathrm{C}$ and the opposite cold-side corner is
$500^\circ\mathrm{C}$. At each active-core elevation, temperature varies linearly across
the duct from the hot side to the cold side.

Above the active core, the cross-sectional temperature distribution remains constant with
axial position.

## Mechanical loading and constraints

No external mechanical load is applied. The duct bottom is fixed against translation in all
three spatial directions. All remaining surfaces are mechanically free.

## Material model

Use isotropic elastic steel with:

- Young's modulus: $1.7\times10^{11}$ Pa;
- Poisson's ratio: 0.30;
- coefficient of linear thermal expansion: $18.0\times10^{-6}\ \mathrm{K}^{-1}$; and
- stress-free temperature: $400^\circ\mathrm{C}$.

The designated reference kinematic formulation uses finite strain.

## Requested quantities of interest

Identify the physics needed to compute lateral displacement of the duct centerline at:

1. $z=2500$ mm — core top;
2. $z=3000$ mm — above-core load-pad elevation; and
3. $z=4000$ mm — duct top.

## Task boundary

Formulate the physical model only. Do not derive a weak form, select MOOSE objects, construct
an input file, choose solver parameters, or perform numerical verification.
