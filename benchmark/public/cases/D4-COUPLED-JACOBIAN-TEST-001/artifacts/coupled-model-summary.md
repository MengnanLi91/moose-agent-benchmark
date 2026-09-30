# Coupled model summary

The reduced fixture contains one temperature variable and one displacement variable. The
temperature equation drives the displacement equation through an off-diagonal coupling.

The observed nonlinear history is compatible with either of two supplied hypotheses:

- **H1:** the residual contains a coupled contribution that is missing from the analytic
  off-diagonal Jacobian block;
- **H2:** the analytic Jacobian is consistent, but the temperature and displacement
  residuals have strongly different scales.

The benchmark asks for a discriminating next test and predicted signatures. It does not ask
for a repair or solver-tuning campaign.
