# Reference solution

Case: `F2-THERMAL-REFLECTOR-001`

## Required answer

The response must provide the following claim values:

```json
{
  "residual_terms": [
    "conduction_volume",
    "prescribed_heat_flux_boundary",
    "convection_boundary"
  ],
  "volume_terms": [
    "integral_Omega_k_grad_T_dot_grad_v"
  ],
  "natural_boundary_terms": [
    "minus_integral_Gamma_q_qcore_v",
    "plus_integral_Gamma_h_h_T_minus_Tinf_v"
  ],
  "essential_boundary_handling": [
    "test_function_zero_on_Gamma_D"
  ],
  "test_function": "temperature_test_function",
  "insulated_boundary": "zero_natural_contribution",
  "residual_expression": "integral_Omega_k_grad_T_dot_grad_v - integral_Gamma_q_qcore_v + integral_Gamma_h_h_T_minus_Tinf_v = 0"
}
```

The evidence record must use `source_id = equation_specification`. A full-credit example is:

```json
{
  "source_id": "equation_specification",
  "observation": "The outward conductive heat flux is q_n = -k grad(T) dot n.",
  "interpretation": "Integration by parts makes the inward prescribed flux negative and the convection residual positive."
}
```

## Governing equation

Temperature $T$ is the only unknown. The steady strong form is

$$
-\nabla\cdot(k\nabla T)=0
\qquad \text{in }\Omega.
$$

The outward conductive heat flux is

$$
q_n=-k\nabla T\cdot\mathbf n.
$$

The supplied natural conditions are $q_n=-q_{\mathrm{core}}$ on $\Gamma_q$,
$q_n=h(T-T_\infty)$ on $\Gamma_h$, and $q_n=0$ on $\Gamma_{\mathrm{ad}}$.
The essential condition is $T=T_D$ on $\Gamma_D$.

## Weak formulation

Let $v$ be a temperature test function satisfying

$$
v=0 \qquad \text{on }\Gamma_D.
$$

Multiplication by $v$ and integration by parts give

$$
\int_\Omega k\nabla T\cdot\nabla v\,d\Omega
-
\int_{\partial\Omega}v\,k\nabla T\cdot\mathbf n\,d\Gamma
=0.
$$

Because $q_n=-k\nabla T\cdot\mathbf n$, the boundary contribution is
$+\int_{\partial\Omega}v q_n\,d\Gamma$. Substitution of the supplied conditions yields

$$
\boxed{
R_T
=
\int_\Omega k\nabla T\cdot\nabla v\,d\Omega
-
\int_{\Gamma_q}q_{\mathrm{core}}v\,d\Gamma
+
\int_{\Gamma_h}h(T-T_\infty)v\,d\Gamma
=0.
}
$$

The insulated boundary contributes zero. No natural residual term is added on
$\Gamma_D$ because the test function vanishes there.

## MOOSE representation

MOOSE object selection is not required and is not graded in this F2 case.

## Task boundary

The required answer is the weak residual and its boundary treatment. Input-file
construction, solver configuration, execution, and numerical verification receive no
credit.

# Grading rubric

## Scoring model

The raw score is 70% capability, 20% evidence, and 10% submission contract:

```text
raw_score = 0.70 * capability + 0.20 * evidence + 0.10 * contract
```

The points below are within their named 100-point component. Passing requires every gate to
pass, capability of at least 80, and a raw score of at least 80. A failed gate makes the
official score zero.

Set-valued criteria use set F1, so missing terms and extra terms both reduce credit.
`normalized_exact` ignores capitalization and repeated whitespace but otherwise requires the
canonical value. The selected residual convention is graded directly; a globally negated
residual is not accepted by the structured fields.

## C1: Residual inventory and diffusion term — 30 capability points

Full credit:
The response lists all three nonzero residual contributions (15 points) and the diffusion
volume term (15 points).

Partial credit:
Both lists use set F1, so correct subsets receive proportional credit and extra terms reduce
precision.

No credit:
Neither the residual inventory nor the volume-term list contains an expected value.

## C2: Natural boundary terms and convection sign — 35 capability points

Full credit:
The natural-term list contains the negative prescribed inward-flux term and positive
convection term (15 points), and the positive convection token passes its separate
20-point membership check.

Partial credit:
An incomplete natural-term list receives set-F1 credit. The separate convection-sign check
is all-or-nothing.

No credit:
Neither natural term is represented correctly.

Common errors:
Using a negative convection term or treating the inward prescribed flux as positive.

## C3: Essential, insulated, and test-function handling — 25 capability points

Full credit:
The test function vanishes on $\Gamma_D$ (10 points), the insulated boundary contributes
zero (10 points), and $v$ is identified as the temperature test function (5 points).

Partial credit:
Each subcriterion scores independently. The essential-condition list uses set F1; the other
two values are normalized exact matches.

No credit:
None of the three expected handling values is present.

## C4: Complete residual expression — 10 capability points

Full credit:
The canonical residual-expression string matches the required volume, negative flux, and
positive convection terms.

Partial credit:
None; this criterion is a normalized exact match.

No credit:
Any term or sign differs from the canonical expression.

Acceptable alternatives:
Equivalent notation may be included in explanatory text, but the structured field must use
the canonical expression shown in the required answer.

## E1: Evidence source — 40 evidence points

Full credit:
The first evidence record uses `source_id = equation_specification`.

No credit:
The source identifier is missing or different.

## E2: Flux observation — 30 evidence points

Full credit:
The observation contains the phrase `outward conductive heat flux`.

No credit:
The observation does not identify the supplied flux convention.

## E3: Derivation interpretation — 30 evidence points

Full credit:
The interpretation contains the phrase `integration by parts`.

No credit:
The interpretation does not connect integration by parts to the boundary signs.

## Submission contract — 100 contract points

The contract component is:

- 40 points after the submission schema and case identity validate;
- 30 points for the fraction of the seven required claim paths that are present;
- 15 points for valid evidence source references and hashes; and
- 15 points for satisfying the no-artifact contract.

Invalid submission identity is rejected before scoring. Evidence and artifact contract
checks are all-or-nothing within their 15-point allocations.

## Gates

The submission must include no artifacts and remain within the declared time, CPU, and
attempt budgets. Failure of either automatic gate sets the official score to zero.
