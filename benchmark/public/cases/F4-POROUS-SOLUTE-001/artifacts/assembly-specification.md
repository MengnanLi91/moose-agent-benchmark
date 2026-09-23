# Porous-Flow Tracer Input-Assembly Specification

## Domain and mesh

Use a one-dimensional saturated porous medium:

$$
0\le x\le80\ \mathrm{m}.
$$

Create a generated one-dimensional mesh with:

```text
xmin = 0
xmax = 80
nx = 80
```

## Variables and initial state

Use nonlinear variables:

```text
porepressure
C
```

where `porepressure` is fluid pore pressure and `C` is tracer mass fraction.

Use:

$$
p(x,0)=1.0\times10^5\ \mathrm{Pa},
\qquad
C(x,0)=0.
$$

Add a constant monomial auxiliary variable named `Darcy_vel_x`.

## Porous medium and fluid

Use one fluid phase and two fluid components. Both nonlinear variables are PorousFlow
variables in this order:

```text
porepressure C
```

Use:

```text
porosity = 0.25
permeability = 2.0e-12 m^2
gravity = '0 0 0'
fluid = water
temperature = 293 K
relative permeability = 1
tortuosity = 0.1
```

The isotropic permeability tensor must have `2.0e-12` on all three diagonal entries and zero
off-diagonal entries.

Use zero molecular diffusion coefficients and:

```text
longitudinal dispersivity = 0.5 m
transverse dispersivity = 0
```

## Boundary conditions

At the left boundary use:

```text
porepressure = 1.2e5 Pa
C = 0.002
```

At the right boundary use:

```text
porepressure = 1.0e5 Pa
tracer = PorousFlow outflow for mass-fraction component 0
```

## Execution controls

Use a transient executioner with:

```text
end_time = 86400000 s
initial dt = 1000 s
dtmax = 432000 s
nl_rel_tol = 1e-6
nl_abs_tol = 1e-12
time stepper = IterationAdaptiveDT
```

Use an SMP preconditioner with full coupling.

## Supplied MOOSE object plan

Use these objects and wire them to the supplied values:

```text
GeneratedMeshGenerator
Variables: porepressure, C
AuxVariable: Darcy_vel_x
PorousFlowDictator
Water97FluidProperties
PorousFlow1PhaseFullySaturated
PorousFlowPorosityConst
PorousFlowPermeabilityConst
PorousFlowSingleComponentFluid
PorousFlowMassFraction
PorousFlowTemperature
PorousFlowDiffusivityConst
PorousFlowRelativePermeabilityConst
PorousFlowMassTimeDerivative
PorousFlowFullySaturatedDarcyFlow
PorousFlowDispersiveFlux
PorousFlowDarcyVelocityComponent
DirichletBC
PorousFlowOutflowBC
PointValue
IterationAdaptiveDT
CSV output
```

Use three flow kernels for fluid component 1 and three tracer kernels for fluid component 0:
mass time derivative, fully saturated Darcy flow, and dispersive flux.

## Required outputs

At $x=40\ \mathrm{m}$, add `PointValue` postprocessors named:

```text
C_midpoint
Darcy_velocity_midpoint
```

The first reports `C`; the second reports `Darcy_vel_x`. Write CSV output.

## Participant artifact

Create `artifacts/solution.i` and return it with artifact role `moose_input`.

The object plan, physics, coefficients, boundaries, execution controls, and outputs are all
supplied. The task is only complete input assembly and parameter/reference wiring.

The accepted object syntax is pinned to MOOSE revision
`c2dfd9fedd3193740a5278ec32269450c618e3b7`.
