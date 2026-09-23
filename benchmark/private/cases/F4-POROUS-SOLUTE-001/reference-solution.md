# Reference solution

Case: `F4-POROUS-SOLUTE-001`

## Required answer

The response must create `artifacts/solution.i`, attach it as exactly one `moose_input`
artifact, and provide:

```json
{
  "assembled_input": true,
  "variables": ["porepressure", "C"],
  "mesh": {
    "dimension": 1,
    "xmin": 0,
    "xmax": 80,
    "nx": 80
  },
  "porous_flow": {
    "porous_flow_vars": ["porepressure", "C"],
    "number_fluid_phases": 1,
    "number_fluid_components": 2
  },
  "properties": {
    "porosity": 0.25,
    "permeability": 2e-12,
    "longitudinal_dispersivity": 0.5
  },
  "boundary_conditions": [
    "inlet_pressure_1.2e5",
    "outlet_pressure_1.0e5",
    "inlet_tracer_0.002",
    "tracer_outflow_component_0"
  ],
  "required_outputs": [
    "C_midpoint",
    "Darcy_velocity_midpoint"
  ],
  "execution": {
    "end_time": 86400000,
    "initial_dt": 1000,
    "dtmax": 432000,
    "time_stepper": "IterationAdaptiveDT"
  }
}
```

Additional claim fields are allowed, but they do not add capability credit.

## Governing model

The model is transient, one-phase, fully saturated porous flow with two fluid components.
`porepressure` represents fluid pressure and `C` represents tracer mass fraction. The
initial conditions are $p=1.0\times10^5\ \mathrm{Pa}$ and $C=0$.

The supplied plan represents accumulation, Darcy advection, and dispersion for fluid
component 1 in the pressure equation and tracer component 0 in the concentration equation.
Porosity, permeability, fluid properties, relative permeability, tortuosity, and
dispersivity are fixed by the public specification.

## Weak formulation

No weak-form derivation is required. The required residual terms are selected already by the
six supplied PorousFlow kernel objects.

## MOOSE representation

The reference input uses:

- `GeneratedMeshGenerator` with `dim = 1`, `xmin = 0`, `xmax = 80`, and `nx = 80`;
- nonlinear variables `porepressure` and `C`;
- constant monomial auxiliary variable `Darcy_vel_x`;
- `PorousFlowDictator` with `porous_flow_vars = 'porepressure C'`, one phase, and two
  components;
- `Water97FluidProperties` and the supplied PorousFlow material objects;
- `PorousFlowMassTimeDerivative`, `PorousFlowFullySaturatedDarcyFlow`, and
  `PorousFlowDispersiveFlux` for each equation;
- `PorousFlowDarcyVelocityComponent` for the x-directed auxiliary velocity;
- pressure and tracer inlet `DirichletBC` objects, outlet pressure `DirichletBC`, and tracer
  `PorousFlowOutflowBC` with `mass_fraction_component = 0`;
- a transient executioner, `IterationAdaptiveDT`, full-coupling `SMP`, midpoint
  `PointValue` postprocessors, and CSV output.

The permeability tensor is isotropic with $2.0\times10^{-12}\ \mathrm{m^2}$ on its diagonal.
The longitudinal dispersivity is $0.5\ \mathrm{m}$ and transverse dispersivity is zero.

## Reference input and outputs

The complete accepted input is `reference.i` in this directory. A participant artifact need
not be byte-for-byte identical, but it must preserve the supplied structure, values, object
references, execution controls, and outputs.

The reference run reaches $t=86400000\ \mathrm{s}$ and produces:

```text
C_midpoint = 0.002
Darcy_velocity_midpoint = 4.9737123050241e-07
```

These values document the validated reference run. The external gates require successful
generation of the named outputs through final time; the structured capability rubric does
not directly compare their numerical values.

## Required evidence

The evidence record must use `source_id = assembly_specification`. A full-credit example is:

```json
{
  "source_id": "assembly_specification",
  "observation": "The model requires one fluid phase and two fluid components.",
  "interpretation": "The submitted input preserves the supplied parameter wiring."
}
```

## Task boundary

Physics selection, weak-form derivation, alternative object selection, and alternative
parameter values are outside this F4 assembly task.

# Grading rubric

## Scoring model

The raw score is 70% capability, 20% evidence, and 10% submission contract:

```text
raw_score = 0.70 * capability + 0.20 * evidence + 0.10 * contract
```

The points below are within their named 100-point component. Passing requires all gates,
capability of at least 80, and a raw score of at least 80. Any failed automatic or external
gate makes the official score zero.

Top-level list criteria use set F1, so missing and extra items reduce credit. Object-valued
criteria use JSON-subset scoring, so expected leaves earn proportional credit and extra keys
do not reduce that criterion. Nested expected lists, such as `porous_flow_vars`, must match
exactly. `assembled_input` is an exact Boolean check.

## C1: Assembly declaration and variables — 15 capability points

Full credit:
`assembled_input` is exactly `true` (5 points), and the variable list contains exactly
`porepressure` and `C` under set-F1 scoring (10 points).

Partial credit:
The declaration and variable list score independently; the list receives proportional
set-F1 credit.

No credit:
The response does not declare an assembled input and identifies neither variable.

## C2: Mesh and porous properties — 30 capability points

Full credit:
The mesh has dimension 1, bounds 0 and 80, and 80 elements (15 points). Porosity is 0.25,
permeability is $2.0\times10^{-12}$, and longitudinal dispersivity is 0.5 (15 points).

Partial credit:
Each criterion uses JSON-subset scoring, so correct expected leaves earn proportional credit.

No credit:
Neither object contains any expected values.

## C3: PorousFlow configuration and boundaries — 30 capability points

Full credit:
The PorousFlow configuration lists both variables, one phase, and two components (15 points).
All four inlet/outlet condition tokens are present (15 points).

Partial credit:
The PorousFlow object earns credit per expected leaf. The boundary list uses set F1.

No credit:
The phase/component wiring and all boundary conditions are incorrect or absent.

Common errors:
Omitting `C` from `porous_flow_vars` or assigning the outflow condition to the wrong
mass-fraction component.

## C4: Outputs and execution controls — 25 capability points

Full credit:
Both midpoint output names are present (15 points), and the execution object contains final
time 86400000, initial step 1000, maximum step 432000, and `IterationAdaptiveDT`
(10 points).

Partial credit:
The output list uses set F1. The execution object earns credit per expected JSON leaf.

No credit:
Neither required output is declared and none of the execution controls matches.

Acceptable alternatives:
Unscored details such as object block names may differ, but the supplied physics, parameter
values, references, output names, and controls must be preserved.

## E1: Evidence source — 40 evidence points

Full credit:
The first evidence record uses `source_id = assembly_specification`.

No credit:
The source identifier is missing or different.

## E2: Component observation — 30 evidence points

Full credit:
The observation contains `one fluid phase and two fluid components`.

No credit:
The observation does not identify both supplied counts.

## E3: Wiring interpretation — 30 evidence points

Full credit:
The interpretation contains the phrase `parameter wiring`.

No credit:
The interpretation does not explain preservation of the supplied wiring.

## Submission contract — 100 contract points

The contract component is:

- 40 points after the submission schema and case identity validate;
- 30 points for the fraction of the eight required claim paths that are present;
- 15 points for valid evidence source references and hashes; and
- 15 points for exactly one verified artifact with role `moose_input`.

Invalid submission identity is rejected before scoring. Evidence and artifact contract
checks are all-or-nothing within their 15-point allocations. A missing, excess, incorrectly
hashed, or incorrectly role-labeled artifact also fails the artifact-policy gate.

## Hard gates

All of the following must pass:

1. **Artifact policy:** exactly one allowed, present, hash-verified `moose_input`.
2. **Usage budget:** declared wall time, CPU time, validation attempts, and execution
   attempts remain within the public limits.
3. **Input validation:** authoritative MOOSE `--check-input` succeeds.
4. **Bounded execution:** the authoritative run completes through final time.
5. **Required output generation:** both midpoint outputs are present through final time.
6. **Semantic preservation:** the artifact preserves all supplied physics, values, and
   references.

No partial gate credit is awarded. Failure of any gate sets the official score to zero.
