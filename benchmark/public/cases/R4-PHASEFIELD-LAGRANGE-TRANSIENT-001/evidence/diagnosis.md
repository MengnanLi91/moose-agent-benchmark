# Supplied diagnosis

The reduced phase-field model completes initial timesteps, then its zero multiplier initialization
and zero Lagrange-constraint regularization produce a transient zero-pivot/SUBPC-equivalent
breakdown. Repair only the multiplier initial value and constraint `epsilon` with small nonzero
values. The physical model, solver, timestep controls, and phase initial fields are frozen.
