# D1 reproduction

Validated on September 29, 2026 with:

- MOOSE commit `c2dfd9fedd3193740a5278ec32269450c618e3b7`;
- PETSc `3.25.2`;
- executable `modules/combined/combined-opt`; and
- one MPI process.

From the public artifact directory:

```bash
"$MOOSE_APP" -i failing.i
```

The expected exit status is 1. The linear `DIVERGED_ITS` event at `dt=2` must precede the
retry at `dt=1`, a second linear failure, and the final `dtmin` termination.
