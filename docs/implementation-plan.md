# MOOSE Agent Benchmark implementation plan

## 1. Implementation objective

The benchmark should measure one MOOSE-native capability at a time while retaining a separate
end-to-end measure of workflow success. The implementation therefore needs four trust boundaries:

1. **Public case contract**: information and actions available to the agent.
2. **Participant workspace**: immutable inputs, mutable artifacts, tool calls, and resource usage.
3. **Private evaluator**: gold criteria, hidden mutants, numerical tolerances, and gate logic.
4. **Result service**: artifact-bound case results and macro-aggregated reports.

The starter implements the contracts, a deterministic structured evaluator, gated scoring,
aggregation, a bounded MOOSE check-input runner, one development case, and CI. It intentionally
does not treat textual similarity to one reference input as proof of correctness.

## 2. Code structure

```text
src/moose_benchmark/
  contracts.py
    CaseContract            Public starting state and action boundary
    EvaluationSpec          Private criteria and gate declarations
    SubmissionEnvelope      Standard participant answer
    BenchmarkManifest       Versioned case registry
    EvaluationContext       Benchmark, submission hash, and artifact workspace binding
    CaseResult              Validated, provenance-bearing evaluator result
  loader.py
    Safe YAML/JSON loading and root-confined path resolution
  comparison.py
    Exact, normalized, set, sequence, subset, and tolerance comparators
  evaluators/
    base.py                 Evaluator protocol
    structured.py           Generic evaluator for atomic structured claims
    __init__.py             Evaluator registry
  scoring.py
    70/20/10 case score, hard-gate application, and macro-aggregation
  runner.py
    Shell-free subprocess invocation with CPU and wall-time limits, plus Linux memory limits
  cli.py
    validate, score, aggregate, and run-check commands
```

The evaluator registry is the extension point. Each new verifier should consume the same case,
submission, and externally measured gate contracts and return the same result envelope.
Evaluator names are registry keys rather than a closed schema literal.

## 3. Case lifecycle

### Authoring

1. Create or select a scientifically accepted base problem.
2. Assign `base_problem_id`, physics-domain labels, target application, and tested build hash.
3. Derive atomic cases by controlling the starting state and scoring only one subcategory.
4. Place prompts and visible artifacts under `benchmark/public`.
5. Place criteria, tolerances, hidden cases, and mutants under `benchmark/private`.
6. Add one gold submission, plausible partial answers, and incorrect mutants.
7. Confirm that the evaluator accepts the gold answer and rejects each mutant for the intended
   reason.

### Execution

1. Create a clean per-request workspace.
2. Materialize only the public case bundle.
3. Record hashes for every supplied artifact.
4. Enforce tool permissions and validation/execution budgets.
5. Store the submitted answer, produced artifacts, tool trace, resource telemetry, target
   application hash, and random seeds.
6. Run private structural, executable, semantic, numerical, and preservation gates.
7. Bind every evaluator result to the submitted artifact hashes.

The scoring CLI rejects case-identity mismatches, rehashes submitted artifacts inside a confined
artifact root, and accepts external gates only when their benchmark version, case ID, and canonical
submission hash match the current request.

### Scoring

For atomic case `i`:

```text
R_i = 0.70 C_i + 0.20 E_i + 0.10 A_i
S_i = G_i R_i
pass_i = G_i and C_i >= 80 and R_i >= 80
```

`G_i` equals one only when every applicable hard gate passes. The result record retains `R_i`
for diagnosis, but leaderboard aggregation uses `S_i`.

Within subcategory `k`:

```text
S_k = mean(S_i for cases assigned to k)
ACS = mean(S_k for F1 through V4)
```

The suite must report missing subcategories during development. Domain generalization uses a
two-stage macro-average across domain-subcategory cells. Integrated workflow cases report
completion rate and first failed stage rather than contributing to ACS.

## 4. Evaluator implementation sequence

### Phase 0: contracts and deterministic core

Implemented in this starter.

- Typed public, private, submission, and result contracts
- Root-confined path handling
- Versioned manifest
- Deterministic criterion comparators
- Gated scoring and aggregation
- Static development case
- GitHub Actions checks for formatting, lint, tests, fixture discrimination, package build, and
  participant-bundle construction

Exit criterion: the gold fixture scores 100, a failed gate produces an official score of zero,
and subcategory macro-averaging resists case-count imbalance.

### Phase 1: MOOSE structural gates

Add evaluator plugins that operate on the exact submitted revision:

- HIT parse result
- Registered object and parameter schema checks
- Variable, function, material, block, and boundary reference checks
- Language-server diagnostics where available
- `--check-input` result and normalized MOOSE failure signature

Store the executable path, application build hash, MOOSE revision, command, exit code, and log
hash with every gate result.

Exit criterion: F4 and R1 cases can receive full credit only after a private rerun validates the
submitted artifact.

### Phase 2: bounded execution and recovery metrics

- Run each candidate in an isolated container or batch allocation.
- Enforce wall time, CPU time, memory, validation attempts, execution attempts, and output size.
- Record nonlinear iterations, linear iterations, timestep cuts, terminal reason, and output
  artifacts.
- Add application-specific command adapters without changing case or result contracts.

Exit criterion: the evaluator can distinguish successful completion, solver failure, timeout,
resource failure, and infrastructure failure.

### Phase 3: semantic and numerical verifiers

Implement plugins for:

- Weak-form term and sign comparison
- MOOSE object-graph equivalence
- Requirement tracing for geometry, materials, BCs/ICs, couplings, and outputs
- MMS error norms and observed spatial or temporal order
- Conservation and invariant checks
- Reference-QoI and uncertainty comparisons
- Solver-error control relative to discretization error

Each plugin should emit typed claims with a status, measured value, tolerance, evidence artifacts,
and reason code. An `inconclusive` result must remain distinct from `failed`.

Exit criterion: verification conclusions can be recomputed from stored output files without using
the agent's reported values.

### Phase 4: mutant library and discrimination tests

For every base problem, create one-factor mutants such as:

- Wrong residual or boundary-flux sign
- Missing material dependency or derivative
- Missing off-diagonal coupling
- Invalid unit scale or material state
- Loose tolerance that hides algebraic error
- Mesh or timestep too coarse for the claimed accuracy
- Missing requested output or changed boundary condition

Track which verifier should reject each mutant. A verifier does not enter authoritative scoring
until it accepts the gold case and rejects its assigned mutants.

Exit criterion: every authoritative verifier has a versioned sensitivity and specificity record
on the curated mutant set.

### Phase 5: benchmark expansion and release

- Add balanced cases across F1 through V4, physics domains, difficulty levels, and root causes.
- Split development, validation, and hidden test sets by `base_problem_id`, not by individual case,
  so sibling cases cannot leak across splits.
- Freeze target application containers and reference-data versions.
- Generate separate participant and evaluator bundles with checksums.
- Produce score vectors, confidence intervals, failure-stage summaries, and cost metrics.

Exit criterion: the release has complete coverage metadata, no base-problem leakage, reproducible
gold results, and a signed immutable manifest.

## 5. Benchmark template rules

An atomic case should declare:

- Exactly one track and subcategory
- The upstream truth supplied to the participant
- Work explicitly excluded from scoring
- Immutable and mutable artifacts
- Permitted and prohibited actions
- Resource and attempt budgets
- Required claim paths and artifact roles
- Private capability criteria whose weights sum to one
- Private evidence criteria whose weights sum to one
- Applicable field or external hard gates

An integrated workflow case should leave `track` and `subcategory` unset, declare the required
stage sequence, and use externally recomputed gates. Integrated workflow completion should never
substitute for the atomic capability profile.

## 6. CI/CD design

### Pull-request pipeline

Run on ordinary hosted runners without MOOSE:

1. Install the Python package.
2. Compile and lint source code.
3. Validate the manifest and all referenced public/private files.
4. Run unit tests for schemas, path confinement, comparators, gates, and aggregation.
5. Score every development gold submission.
6. Require gold answers to pass and designated mutants to fail.
7. Build the Python package and participant bundle.

### MOOSE integration pipeline

Run on a self-hosted runner or approved container image:

1. Verify the target application build hash.
2. Run `--check-input` for valid reference cases.
3. Run bounded probe executions for selected cases.
4. Execute gold and mutant matrices.
5. Compare normalized results with stored tolerances.
6. Upload logs and numerical artifacts even when a case fails.

The starter marks this job as opt-in because a generic hosted runner does not contain the required
MOOSE applications.

### Release pipeline

On a signed version tag:

1. Require the pull-request and MOOSE integration pipelines to pass.
2. Freeze manifest, artifact hashes, application/container digests, and evaluator versions.
3. Build a public participant bundle that excludes `benchmark/private`.
4. Build a protected evaluator bundle.
5. Publish checksums, schema versions, and a machine-readable coverage report.

## 7. Immediate next cases

Use one nonlinear radiation base problem to exercise the complete authoring path:

- F2: derive the nonlinear natural boundary residual.
- F3: map residual terms to MOOSE objects and dependencies.
- D3: localize a reversed radiation-flux sign.
- R2: repair the supplied sign defect without changing other BCs.
- V3: close the global energy balance.
- V4: compare surface-temperature QoIs with the external reference.

These sibling cases should share a `base_problem_id` but remain isolated in scoring and dataset
splits.
