# Reference solution

Case: `F4-POROUS-SOLUTE-001`

## Required answer

The runner-owned submission must contain `artifacts/solution.i` as the `moose_input` artifact. The input itself must preserve the supplied mesh, variables, PorousFlow configuration, properties, boundary conditions, outputs, and execution controls. Explanatory Markdown is optional.

## Governing model

The model is transient, one-phase, fully saturated porous flow with two fluid components.
`porepressure` represents fluid pressure and `C` represents tracer mass fraction. The
initial conditions are $p=1.0\times10^5\ \mathrm{Pa}$ and $C=0$.

The supplied plan represents accumulation, Darcy advection, and dispersion for fluid
component 1 in the pressure equation and tracer component 0 in the concentration equation.
Porosity, permeability, fluid properties, relative permeability, tortuosity, and
dispersivity are fixed by the public specification.

## Weak formulation

No weak-form derivation is required. The required residual terms are selected already by the
six supplied PorousFlow kernel objects.

## MOOSE representation

The reference input uses:

- `GeneratedMeshGenerator` with `dim = 1`, `xmin = 0`, `xmax = 80`, and `nx = 80`;
- nonlinear variables `porepressure` and `C`;
- constant monomial auxiliary variable `Darcy_vel_x`;
- `PorousFlowDictator` with `porous_flow_vars = 'porepressure C'`, one phase, and two
  components;
- `Water97FluidProperties` and the supplied PorousFlow material objects;
- `PorousFlowMassTimeDerivative`, `PorousFlowFullySaturatedDarcyFlow`, and
  `PorousFlowDispersiveFlux` for each equation;
- `PorousFlowDarcyVelocityComponent` for the x-directed auxiliary velocity;
- pressure and tracer inlet `DirichletBC` objects, outlet pressure `DirichletBC`, and tracer
  `PorousFlowOutflowBC` with `mass_fraction_component = 0`;
- a transient executioner, `IterationAdaptiveDT`, full-coupling `SMP`, midpoint
  `PointValue` postprocessors, and CSV output.

The permeability tensor is isotropic with $2.0\times10^{-12}\ \mathrm{m^2}$ on its diagonal.
The longitudinal dispersivity is $0.5\ \mathrm{m}$ and transverse dispersivity is zero.

## Reference input and outputs

The complete accepted input is `reference.i` in this directory. A participant artifact need
not be byte-for-byte identical, but it must preserve the supplied structure, values, object
references, execution controls, and outputs.

The reference run reaches $t=86400000\ \mathrm{s}$ and produces:

```text
C_midpoint = 0.002
Darcy_velocity_midpoint = 4.9737123050241e-07
```

These values document the validated reference run. The external gates require successful
generation of the named outputs through final time; the semantic capability rubric does
not directly compare their numerical values.

## Task boundary

The submitted MOOSE input is the graded F4 artifact. Explanatory prose is optional and cannot substitute for correct HIT structure and wiring.

# Semantic grading and gates

The private rubric evaluates the actual `solution.i`. Runner-owned integrity, MOOSE input validation, bounded execution, output generation, and semantic-preservation checks remain hard gates.
