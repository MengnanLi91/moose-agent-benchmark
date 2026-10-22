# Problem specification

On $\Omega=[0,1]^2$, solve steady heat conduction and plane-strain thermoelasticity:

$$
-\nabla^2T=Q,\qquad
-\nabla\cdot\boldsymbol\sigma=\mathbf b,
$$

$$
\boldsymbol\sigma=\mathsf C:\left(\boldsymbol\varepsilon-\alpha T\mathbf I\right),
\qquad
\boldsymbol\varepsilon=\tfrac12(\nabla\mathbf u+\nabla\mathbf u^T).
$$

Use $\lambda=2$, $\mu=3$, $\alpha=0.01$, stress-free temperature zero, and

$$
T^*=\sin(\pi x)\sin(\pi y),\quad
u_x^*=\sin(\pi x)\sin(\pi y),\quad
u_y^*=\sin(\pi y)\cos(\pi x).
$$

Derive $Q$, the in-plane stress components under the stated plane-strain convention, $b_x$, $b_y$, and all temperature and displacement boundary values.
