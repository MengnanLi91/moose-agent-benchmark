# MMS implementation specification

On $\Omega=[0,1]^2$, solve steady incompressible Navier–Stokes with $\rho=\mu=1$:

$$
\nabla\cdot\mathbf u=0,
\qquad
(\mathbf u\cdot\nabla)\mathbf u-\nabla^2\mathbf u+\nabla p=\mathbf f.
$$

Use

$$
u^*=\sin(\pi x)\cos(\pi y),\quad
v^*=-\cos(\pi x)\sin(\pi y),\quad
p^*=\cos(2\pi x)+\cos(2\pi y),
$$

$$
f_x=2\pi^2\sin(\pi x)\cos(\pi y)-1.5\pi\sin(2\pi x),
$$

$$
f_y=-2\pi^2\cos(\pi x)\sin(\pi y)-1.5\pi\sin(2\pi y).
$$

Use field names `u`, `v`, and `p`; Taylor–Hood Q2/Q1 elements; exact velocity boundaries; and a zero-mean pressure constraint. Preserve the protected exact functions, pressure integral, error postprocessors, and output block from `input-scaffold.i`.

Use $N\in\{4,8,16,32\}$. Report order three for velocity and order two for pressure.
