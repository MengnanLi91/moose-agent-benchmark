# Supplied diagnosis

The supplied parsed material depends on the existing nonlinear `temperature` variable, but that
dependency is not declared in the material's input configuration. Consequently, the expression
parser reports an unknown identifier before the solve.

The expression, variables, kernels, mesh, boundary conditions, and solver configuration are
already correct and frozen. Repair only the coupled-variable declaration on
`Materials/dependent_diffusivity`.
