# D2 reproduction

Validated on September 29, 2026 with MOOSE commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`,
`modules/combined/combined-opt`, and one MPI process.

From the public artifact directory:

```bash
"$MOOSE_APP" -i failing.i
```

The expected exit status is 1. Confirm that the initial and final residuals reproduce the
three public inequalities before updating any evidence.
