# D4 hypothesis reproductions

Validated on September 29, 2026 with MOOSE commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`,
`modules/combined/combined-opt`, and one MPI process.

From `variants/`, run:

```bash
"$MOOSE_APP" -i h1-missing-offdiag.i
"$MOOSE_APP" -i h2-poor-scaling.i
```

Both variants include `-snes_test_jacobian`, `-snes_test_jacobian_view`, and
`-snes_force_iteration`, and both preserve a large initial temperature-to-displacement
residual-scale difference.

H1 uses `MatCoupledForce` with a temperature-dependent non-AD material property. The
residual includes that dependence while the analytic off-diagonal omits its derivative.
H2 uses a consistently differentiated coupled force with the same intentionally imbalanced
thermal and mechanical source scales.
