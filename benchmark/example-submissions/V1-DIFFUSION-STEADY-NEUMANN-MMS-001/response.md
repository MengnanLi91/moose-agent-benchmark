# Canonical derivation

For $u^*=\cos(\pi x)\cos(\pi y)+2$,

$$
\nabla u^*=\left(-\pi\sin(\pi x)\cos(\pi y),
-\pi\cos(\pi x)\sin(\pi y)\right),
$$

$$
\nabla^2u^*=-2\pi^2\cos(\pi x)\cos(\pi y).
$$

Thus

$$
s=2\pi^2\cos(\pi x)\cos(\pi y).
$$

Both gradient components vanish on their corresponding pair of sides, so $g=\nabla u^*\cdot\mathbf n=0$ on the entire boundary. The oscillatory term has zero integral and the unit square has area one, hence

$$
\frac{1}{|\Omega|}\int_\Omega u^*\,d\Omega=2.
$$

Finally, $\int_\Omega s\,d\Omega=0=-\int_{\partial\Omega}g\,d\Gamma$, which satisfies the compatibility condition for $-\nabla^2u=s$.
