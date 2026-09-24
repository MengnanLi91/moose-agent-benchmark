# Split Cahn-Hilliard object map

Use `TimeDerivative` on variable `c` for the concentration time derivative. Use `SplitCHWRes` on
`mu` with `mob_name = M`, and use `SplitCHParsed` on `c` with `w = mu`, `f_name = F`, and
`kappa_name = kappa`.

Define `F` with `DerivativeParsedMaterial` and define constant `M` and `kappa` properties. This
incorrectly contributes the time derivative to the `c` residual instead of coupling it into the
`mu` residual.
