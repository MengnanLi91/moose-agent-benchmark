# Split Cahn-Hilliard object map

| Weak contribution | Residual variable | MOOSE object | Required wiring |
|---|---|---|---|
| Time derivative of concentration $c$ | `mu` | `CoupledTimeDerivative` | `v = c` |
| Chemical-potential gradient | `mu` | `SplitCHWRes` | `mob_name = M` |
| Concentration/free-energy relation | `c` | `SplitCHParsed` | `w = mu`, `f_name = F`, `kappa_name = kappa` |

Here `c` is concentration and `mu` is chemical potential. Define `F` with a
`DerivativeParsedMaterial` coupled to `c`. Define the constant properties `M` and `kappa` with a
constant-property material. The map therefore includes both the $c$ time derivative coupled into
the `mu` residual and `mu` coupled into the concentration relation.
