# Canonical derivation

Let $s_x=\sin(\pi x)$, $c_x=\cos(\pi x)$, $s_y=\sin(\pi y)$, and $c_y=\cos(\pi y)$. The nonzero strains are

$$
\varepsilon_{xx}=\pi c_xs_y,\qquad
\varepsilon_{yy}=\pi c_xc_y,\qquad
\varepsilon_{xy}=\frac{\pi}{2}s_x(c_y-s_y).
$$

For $\lambda=2$ and $\mu=3$,

$$
\sigma_{xx}=8\pi c_xs_y+2\pi c_xc_y,
$$

$$
\sigma_{yy}=2\pi c_xs_y+8\pi c_xc_y,
\qquad
\sigma_{xy}=3\pi s_x(c_y-s_y).
$$

Using $\mathbf b=-\nabla\cdot\boldsymbol\sigma$ gives

$$
b_x=11\pi^2s_xs_y+5\pi^2s_xc_y,
$$

$$
b_y=11\pi^2s_yc_x+5\pi^2c_xc_y.
$$

The displacement Dirichlet data equal the supplied exact fields. In particular, $u_x^*=0$ on every side; $u_y^*=0$ on $y=0,1$, $u_y^*=\sin(\pi y)$ on $x=0$, and $u_y^*=-\sin(\pi y)$ on $x=1$.
