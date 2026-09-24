# Physics specification

The solved primary fields are the three displacement components $u_x$, $u_y$, and $u_z$.
Temperature is a prescribed spatial field rather than another solved variable.

The duct satisfies quasi-static balance of linear momentum with finite-strain kinematics.
The material is isotropic linear elastic, closed by Young's modulus and Poisson ratio. Thermal
expansion enters through an eigenstrain

$$
\boldsymbol{\epsilon}_{\mathrm{th}}
= \alpha (T-T_{\mathrm{sf}})\mathbf{I},
$$

using the supplied thermal-expansion coefficient and stress-free temperature.

All displacement components are fixed at the bottom. The remaining surfaces are traction free.
The requested quantities are lateral centerline displacements at the core top, ACLP, and duct top.
