# Weak residual

Let $v$ be a temperature test function with $v=0$ on $\Gamma_D$. Integrating conduction by
parts and using the supplied outward conductive flux convention gives

$$
R(T;v)
= \int_{\Omega} k\nabla T\cdot\nabla v\,d\Omega
- \int_{\Gamma_q} q_{\mathrm{core}}v\,d\Gamma
+ \int_{\Gamma_h} h(T-T_{\infty})v\,d\Gamma
=0.
$$

The insulated boundary $\Gamma_{\mathrm{ad}}$ contributes no natural boundary term. Thus the
residual contains the conduction volume contribution, inward prescribed-flux contribution, and
positive convection contribution under the stated outward-normal convention.
