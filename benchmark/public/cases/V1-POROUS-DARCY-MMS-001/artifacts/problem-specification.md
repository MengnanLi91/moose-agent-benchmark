# MMS implementation specification

On $\Omega=[0,1]^2$, implement a one-phase, one-component fully saturated PorousFlow problem:

$$
-\nabla\cdot\left(\kappa\nabla p\right)=q,
\qquad
\kappa=1+\frac{x}{4},
\qquad
p^*=1+\sin(\pi x)\sin(\pi y),
$$

with unit viscosity, zero gravity, and

$$
q=2\pi^2\left(1+\frac{x}{4}\right)\sin(\pi x)\sin(\pi y)
-\frac{\pi}{4}\cos(\pi x)\sin(\pi y).
$$

Use field name `p`, first-order Lagrange elements, PorousFlow Darcy flow and material objects, exact Dirichlet data, and the protected blocks in `input-scaffold.i`.

Use $N\in\{8,16,32,64\}$ and report spatial $L^2(p)$ convergence of order two.
