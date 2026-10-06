# Reproduction record

## Mechanism

The zero multiplier and zero regularization complete times 1 and 2, then fail during time 3 with DIVERGED_PC_FAILED and FACTOR_NUMERIC_ZEROPIVOT. Small nonzero values complete time 10.

## Environment

- MOOSE commit: `c2dfd9fedd3193740a5278ec32269450c618e3b7`
- Base executable SHA-256: `3be083e88c63c265e1c98a3f0cbd401fb2d7feb39547c6fa22ff1cb2f4f34472`
- PETSc: `3.25.2`
- Compiler: `clang 19.1.7 (arm64-apple-darwin20.0.0)`
- Processes: `1`
- Required environment: `FI_PROVIDER=tcp`

## Command

`combined-opt -i solution.i`

## Repetitions

- Faulty: exit 1 at time step 3 in all three runs.
- Gold: exit 0 at time 10 in all three runs.

The fixture is an original reduction of the discussion mechanism. Logs and CSV outputs from all six runs are stored in `validation/`. Exact accepted ranges and tolerance floors remain private.
