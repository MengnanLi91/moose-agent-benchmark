# D2 Task — Reconstruct the Nonlinear Convergence Chain

Inspect the immutable thermal input and residual report. Reconstruct the ordered causal chain
that explains why the run reports nonlinear nonconvergence even though the final residual is
below $10^{-6}$.

Return:

- `claim.causal_chain`: an ordered list of stable causal identifiers;
- `claim.computed_relative_target`: the target obtained from the recorded initial residual
  and `nl_rel_tol`; and
- `claim.terminal_symptom`: a stable terminal identifier.

Use the following causal identifiers when applicable:

- `initial_residual_sets_relative_target`
- `linear_solve_reduces_residual_but_stops`
- `final_residual_exceeds_both_nonlinear_targets`
- `nonlinear_iteration_limit_reached`

Include one evidence entry citing `residual_report`. Treat `nl_rel_tol` as a multiplier on
the initial nonlinear residual, not as an absolute $10^{-6}$ threshold. Do not repair or
rerun the input.
