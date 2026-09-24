# Reference solution

Case: `F2-THERMAL-REFLECTOR-001`

## Required answer

A full-credit response derives the complete residual with the diffusion volume term, prescribed-flux and convection boundary terms, essential and insulated boundary handling, integration regions, and temperature test function. Equivalent mathematical notation is accepted.

## Governing equation

Temperature $T$ is the only unknown. The steady strong form is

$$
-\nabla\cdot(k\nabla T)=0
\qquad \text{in }\Omega.
$$

The outward conductive heat flux is

$$
q_n=-k\nabla T\cdot\mathbf n.
$$

The supplied natural conditions are $q_n=-q_{\mathrm{core}}$ on $\Gamma_q$,
$q_n=h(T-T_\infty)$ on $\Gamma_h$, and $q_n=0$ on $\Gamma_{\mathrm{ad}}$.
The essential condition is $T=T_D$ on $\Gamma_D$.

## Weak formulation

Let $v$ be a temperature test function satisfying

$$
v=0 \qquad \text{on }\Gamma_D.
$$

Multiplication by $v$ and integration by parts give

$$
\int_\Omega k\nabla T\cdot\nabla v\,d\Omega
-
\int_{\partial\Omega}v\,k\nabla T\cdot\mathbf n\,d\Gamma
=0.
$$

Because $q_n=-k\nabla T\cdot\mathbf n$, the boundary contribution is
$+\int_{\partial\Omega}v q_n\,d\Gamma$. Substitution of the supplied conditions yields

$$
\boxed{
R_T
=
\int_\Omega k\nabla T\cdot\nabla v\,d\Omega
-
\int_{\Gamma_q}q_{\mathrm{core}}v\,d\Gamma
+
\int_{\Gamma_h}h(T-T_\infty)v\,d\Gamma
=0.
}
$$

The insulated boundary contributes zero. No natural residual term is added on
$\Gamma_D$ because the test function vanishes there.

## MOOSE representation

MOOSE object selection is not required and is not graded in this F2 case.

## Task boundary

The required answer is the weak residual and its boundary treatment. Input-file
construction, solver configuration, execution, and numerical verification receive no
credit.

# Semantic grading

The private rubric grades the complete derivation, including signs, integration regions, and test-function factors. Equivalent notation, term ordering, and internally consistent sign conventions are accepted.
