# Reference solution

Case: `F3-PHASEFIELD-SPLITCH-001`

## Required answer

A full-credit response maps every supplied weak term to the correct MOOSE object, residual variable, coupling, parameter name, and material property. Prose, tables, or lists are accepted, and mapping order is not scored.

## Governing equations

The two nonlinear variables are concentration $c$ and chemical potential $\mu$. The supplied
free energy and constants are

$$
f(c)=Wc^2(1-c)^2,\qquad W=1,\qquad \kappa=2,\qquad M=1.
$$

The split Cahn-Hilliard system uses the concentration evolution equation and a
chemical-potential/free-energy relation.

## Weak formulation

Find $c$ and $\mu$ such that

$$
R_\mu
=
\left(\frac{\partial c}{\partial t},\psi_\mu\right)
+
\left(M\nabla\mu,\nabla\psi_\mu\right)
=0
$$

and

$$
R_c
=
\left(
-\kappa\nabla^2c
+
\frac{\partial f}{\partial c}
-
\mu,
\psi_c
\right)
=0.
$$

Natural zero-flux boundary conditions are already supplied and need no additional mapping in
the response.

## MOOSE representation

The term $(\partial c/\partial t,\psi_\mu)$ maps to `CoupledTimeDerivative` on
`variable = mu` with `v = c`. This cross-variable placement is the central requirement.

The term $(M\nabla\mu,\nabla\psi_\mu)$ maps to `SplitCHWRes` on `variable = mu` with
`mob_name = M`.

The concentration/free-energy relation maps to `SplitCHParsed` on `variable = c`, coupled
through `w = mu`, with `f_name = F` and `kappa_name = kappa`.

The free energy uses `DerivativeParsedMaterial` because derivatives with respect to $c$ are
required. `M` and `kappa` are constant properties and may be supplied by
`GenericConstantMaterial`.

## Task boundary

Only the F3 object and coupling map is graded. Prose, tables, and lists are equally acceptable; a complete input file is outside scope.

# Semantic grading

The private rubric evaluates object choices, residual ownership, material properties, and couplings without requiring a prescribed mapping schema.
