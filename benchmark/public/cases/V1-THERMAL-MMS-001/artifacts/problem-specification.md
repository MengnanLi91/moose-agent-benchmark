# MMS implementation specification

On $\Omega=[0,1]^2$ for $0\le t\le1$, solve

$$
T_t-\nabla^2T=Q,
\qquad
T^*=e^{-t}\sin(\pi x)\sin(\pi y),
$$

with

$$
Q=(-1+2\pi^2)e^{-t}\sin(\pi x)\sin(\pi y).
$$

Use field name `T`, first-order Lagrange elements, a `FunctionIC`, homogeneous Dirichlet boundaries, `TimeDerivative`, `Diffusion`, `BodyForce`, and backward Euler. Preserve the exact-function, error, and output blocks from `input-scaffold.i` exactly.

Use $n=128$ and $\Delta t\in\{0.2,0.1,0.05,0.025\}$ through final time 1. Report final-time $L^2(T)$ errors and first-order temporal convergence.
