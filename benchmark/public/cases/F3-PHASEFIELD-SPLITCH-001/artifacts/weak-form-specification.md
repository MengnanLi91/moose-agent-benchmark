# Split Cahn-Hilliard Weak-Form Specification

## Variables

Use two nonlinear variables:

- $c$: concentration;
- $\mu$: chemical potential.

## Free energy and coefficients

$$
f(c)=Wc^2(1-c)^2,
\qquad W=1.
$$

The gradient-energy coefficient and mobility are

$$
\kappa=2,
\qquad M=1.
$$

## Supplied weak formulation

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

Natural zero-flux boundary conditions are used.

## Permitted MOOSE object registry

The object map must use only these object types:

```text
CoupledTimeDerivative
SplitCHWRes
SplitCHParsed
DerivativeParsedMaterial
GenericConstantMaterial
ConstantMaterial
```

The accepted registry and parameter names are pinned to MOOSE revision
`c2dfd9fedd3193740a5278ec32269450c618e3b7`.

## Required mapping detail

For each weak-form term, identify:

- the MOOSE object;
- the nonlinear variable receiving the residual;
- coupled variables;
- required material-property names;
- relevant object parameters.

Do not derive the weak form or write a complete MOOSE input file.
