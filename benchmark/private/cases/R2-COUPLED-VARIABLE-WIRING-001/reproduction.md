# Reproduction record

## Mechanism

The parsed material expression references the existing nonlinear `temperature` variable without
declaring it in `coupled_variables`. MOOSE rejects the expression with `Syntax error: Unknown
identifier`. Adding only the missing declaration allows input validation and the steady coupled
diffusion solve to complete.

The fixture is an original reduction of the input-configuration mechanism discussed in MOOSE
Discussion 28157. No discussion input or attachment was copied.

## Environment

- MOOSE commit: `c2dfd9fedd3193740a5278ec32269450c618e3b7`
- Base executable SHA-256: `3be083e88c63c265e1c98a3f0cbd401fb2d7feb39547c6fa22ff1cb2f4f34472`
- PETSc: `3.25.2`
- Compiler used for the prebuilt executable: `clang 19.1.7 (arm64-apple-darwin20.0.0)`
- Processes: `1`
- Local validation environment: `FI_PROVIDER=tcp`
- Source retrieved: `2026-10-06`

## Commands

- Input validation: `combined-opt --check-input -i solution.i`
- Authoritative run: `combined-opt -i solution.i`
- Scope: `hit diff failing.i solution.i`
- Coupling lookup: `hit find Materials/dependent_diffusivity/coupled_variables solution.i`

## Repetitions

- Faulty: exit 1 with `Syntax error: Unknown identifier` in all three runs.
- Gold: exit 0 with `Solve Converged` and identical QoIs in all three runs.

Logs and CSV outputs are stored in `validation/`. Exact tolerance floors remain private.
