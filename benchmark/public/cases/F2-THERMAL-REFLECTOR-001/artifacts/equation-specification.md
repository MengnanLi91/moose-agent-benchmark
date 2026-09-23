# Strong-Form Thermal Problem

## Domain and unknown

Consider a steady graphite reflector domain $\Omega$. Temperature
$T(\mathbf{x})$ is the only unknown. Thermal conductivity is constant:

$$
k = 25\ \mathrm{W/(m\,K)}.
$$

There is no volumetric heat generation.

## Governing equation

$$
-\nabla\cdot(k\nabla T)=0
\qquad \text{in }\Omega.
$$

## Boundary decomposition

$$
\partial\Omega
=
\Gamma_q \cup \Gamma_h \cup \Gamma_D \cup \Gamma_{\mathrm{ad}}.
$$

Define outward conductive heat flux by

$$
q_n=-k\nabla T\cdot\mathbf n.
$$

### Pebble-bed-facing surface

An inward heat flux is prescribed on $\Gamma_q$:

$$
q_n=-q_{\mathrm{core}},
\qquad
q_{\mathrm{core}}=5000\ \mathrm{W/m^2}.
$$

### Barrel surface

Convective cooling is applied on $\Gamma_h$:

$$
-k\nabla T\cdot\mathbf n=h(T-T_\infty),
$$

with $h=10\ \mathrm{W/(m^2K)}$ and $T_\infty=300\ \mathrm{K}$.

### Fluid-solid interface

Temperature is prescribed on $\Gamma_D$:

$$
T=T_D(\mathbf{x}).
$$

### Symmetry, top, and bottom surfaces

These surfaces are insulated:

$$
-k\nabla T\cdot\mathbf n=0
\qquad \text{on }\Gamma_{\mathrm{ad}}.
$$

## Task boundary

Derive only the finite-element weak residual and boundary treatment. Do not select MOOSE
objects, write an input file, choose a solver, or execute the problem.
