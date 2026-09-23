# Reference solution

Case: `F3-PHASEFIELD-SPLITCH-001`

## Required answer

The residual mappings must appear in the order shown:

```json
{
  "variables": {
    "c": "concentration",
    "mu": "chemical_potential"
  },
  "residual_object_map": [
    {
      "term": "concentration_time_derivative",
      "object": "CoupledTimeDerivative",
      "variable": "mu",
      "v": "c"
    },
    {
      "term": "chemical_potential_gradient",
      "object": "SplitCHWRes",
      "variable": "mu",
      "mob_name": "M"
    },
    {
      "term": "free_energy_gradient_relation",
      "object": "SplitCHParsed",
      "variable": "c",
      "w": "mu",
      "f_name": "F",
      "kappa_name": "kappa"
    }
  ],
  "materials": [
    {
      "object": "DerivativeParsedMaterial",
      "property_name": "F",
      "coupled_variables": ["c"],
      "expression": "W*c^2*(1-c)^2"
    },
    {
      "object": "GenericConstantMaterial",
      "prop_names": ["M", "kappa"],
      "prop_values": [1.0, 2.0]
    }
  ],
  "couplings": [
    "c_time_derivative_to_mu_residual",
    "mu_to_c_split_ch_relation"
  ]
}
```

Only the expected subset of the material entries is scored, but the complete wiring above is
the reference answer.

## Governing equations

The two nonlinear variables are concentration $c$ and chemical potential $\mu$. The supplied
free energy and constants are

$$
f(c)=Wc^2(1-c)^2,\qquad W=1,\qquad \kappa=2,\qquad M=1.
$$

The split Cahn-Hilliard system uses the concentration evolution equation and a
chemical-potential/free-energy relation.

## Weak formulation

Find $c$ and $\mu$ such that

$$
R_\mu
=
\left(\frac{\partial c}{\partial t},\psi_\mu\right)
+
\left(M\nabla\mu,\nabla\psi_\mu\right)
=0
$$

and

$$
R_c
=
\left(
-\kappa\nabla^2c
+
\frac{\partial f}{\partial c}
-
\mu,
\psi_c
\right)
=0.
$$

Natural zero-flux boundary conditions are already supplied and need no additional mapping in
the structured response.

## MOOSE representation

The term $(\partial c/\partial t,\psi_\mu)$ maps to `CoupledTimeDerivative` on
`variable = mu` with `v = c`. This cross-variable placement is the central requirement.

The term $(M\nabla\mu,\nabla\psi_\mu)$ maps to `SplitCHWRes` on `variable = mu` with
`mob_name = M`.

The concentration/free-energy relation maps to `SplitCHParsed` on `variable = c`, coupled
through `w = mu`, with `f_name = F` and `kappa_name = kappa`.

The free energy uses `DerivativeParsedMaterial` because derivatives with respect to $c$ are
required. `M` and `kappa` are constant properties and may be supplied by
`GenericConstantMaterial`.

## Required evidence

The evidence record must use `source_id = weak_form_specification`. A full-credit example is:

```json
{
  "source_id": "weak_form_specification",
  "observation": "The time derivative of c appears in the equation tested by the chemical-potential test function.",
  "interpretation": "CoupledTimeDerivative contributes that term to the mu residual."
}
```

## Task boundary

The participant maps the supplied weak terms to the permitted registry. Rederiving the
physics, adding unlisted object types, writing a complete input, selecting solvers, and
executing the model are not graded.

# Grading rubric

## Scoring model

The raw score is 70% capability, 20% evidence, and 10% submission contract:

```text
raw_score = 0.70 * capability + 0.20 * evidence + 0.10 * contract
```

The points below are within their named 100-point component. Passing requires all gates,
capability of at least 80, and a raw score of at least 80.

Object and material mappings use JSON-subset scoring: expected leaves earn proportional
credit, and extra unscored keys do not reduce that criterion. The coupling list uses set F1,
so omissions and extra entries both reduce credit.

## C1: Variables — 10 capability points

Full credit:
`c` maps to concentration and `mu` maps to chemical potential.

Partial credit:
JSON-subset scoring awards one-half credit when only one mapping is correct.

No credit:
Neither variable meaning is correct.

## C2: Coupled time derivative — 40 capability points

Full credit:
The first residual entry identifies `concentration_time_derivative`,
`CoupledTimeDerivative`, `variable = mu`, and `v = c`.

Partial credit:
Each expected JSON leaf contributes proportionally.

No credit:
The first residual entry is missing or has no expected values.

Common errors:
Using `TimeDerivative` on `c`, or putting `CoupledTimeDerivative` on `variable = c`.

## C3: Remaining residual maps — 25 capability points

Full credit:
The second entry maps the chemical-potential gradient to `SplitCHWRes` with
`variable = mu` and `mob_name = M` (10 points). The third maps the free-energy relation to
`SplitCHParsed` with `variable = c`, `w = mu`, `f_name = F`, and
`kappa_name = kappa` (15 points).

Partial credit:
Each entry uses JSON-subset scoring, so correct leaves earn proportional credit.

No credit:
Neither residual entry contains the expected mapping.

## C4: Derivative-capable free-energy material — 15 capability points

Full credit:
The first material entry uses `DerivativeParsedMaterial`, `property_name = F`, and
`coupled_variables = ["c"]`.

Partial credit:
Correct JSON leaves earn proportional credit.

No credit:
The first material entry does not identify any expected material wiring.

Common errors:
Using a non-derivative material for $F$. The constant-property material is part of the
reference answer but is not a separate capability criterion.

## C5: Cross-variable couplings — 10 capability points

Full credit:
Both `c_time_derivative_to_mu_residual` and `mu_to_c_split_ch_relation` are listed.

Partial credit:
Set F1 gives proportional credit for a partial or overinclusive list.

No credit:
Neither coupling is identified.

## E1: Evidence source — 40 evidence points

Full credit:
The first evidence record uses `source_id = weak_form_specification`.

No credit:
The source identifier is missing or different.

## E2: Time-term observation — 30 evidence points

Full credit:
The observation contains the phrase `time derivative of c`.

No credit:
The observation does not identify the supplied coupled time term.

## E3: Residual interpretation — 30 evidence points

Full credit:
The interpretation contains the phrase `mu residual`.

No credit:
The interpretation does not connect the term to the chemical-potential residual.

## Submission contract — 100 contract points

The contract component is:

- 40 points after the submission schema and case identity validate;
- 30 points for the fraction of the four required claim paths that are present;
- 15 points for valid evidence source references and hashes; and
- 15 points for satisfying the no-artifact contract.

Invalid submission identity is rejected before scoring. Evidence and artifact contract
checks are all-or-nothing within their 15-point allocations.

## Gates

The submission must include no artifacts and remain within the declared time, CPU, and
attempt budgets. Failure of either automatic gate sets the official score to zero.
