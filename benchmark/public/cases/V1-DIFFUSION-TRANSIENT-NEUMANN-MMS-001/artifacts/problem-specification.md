# MMS implementation specification

On $\Omega=[0,1]^2$ solve

$$
u_t-\nabla^2u=0
$$

with homogeneous Neumann boundaries and

$$
u^*=2+e^{-2\pi^2t}\cos(\pi x)\cos(\pi y).
$$

Use first-order Lagrange elements, `TimeDerivative`, `Diffusion`, a `FunctionIC`, backward Euler, final time $0.05$, and field name `u`. Preserve the exact-function, error, mean, and output blocks from `input-scaffold.i` exactly.

Run with $n=128$ and $\Delta t\in\{0.005,0.0025,0.00125,0.000625\}$. Report final-time $L^2(u)$ errors and first-order temporal convergence. The domain mean must remain 2 at every recorded row.
