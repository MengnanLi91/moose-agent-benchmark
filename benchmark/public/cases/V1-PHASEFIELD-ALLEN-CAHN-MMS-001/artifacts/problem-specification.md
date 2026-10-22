# MMS implementation specification

On $\Omega=[0,1]^2$ for $0\le t\le1$, implement

$$
\eta_t+M\left(F'(\eta)-\kappa\nabla^2\eta\right)=s,
$$

with $M=1$, $\kappa=0.01$, $F(\eta)=\eta^2(1-\eta)^2$, and

$$
\eta^*=\frac12+0.1e^{-t}\sin(\pi x)\sin(\pi y).
$$

Writing $a=0.1e^{-t}\sin(\pi x)\sin(\pi y)$, use

$$
s=(-2+0.02\pi^2)a+4a^3.
$$

Use field name `eta`, first-order Lagrange elements, the MOOSE Allen–Cahn bulk and interface kernels, a `FunctionIC`, exact Dirichlet data, backward Euler, and the protected blocks in `input-scaffold.i`.

Use $n=128$ and $\Delta t\in\{0.1,0.05,0.025,0.0125\}$. Report first-order final-time $L^2(\eta)$ convergence.
