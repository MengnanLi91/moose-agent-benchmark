# MOOSE Agent Benchmark starter

This repository is a runnable starting point for evaluating MOOSE agents across four
separate capabilities:

- `FORM`: physics-to-MOOSE formulation
- `DIAG`: MOOSE-native error analysis
- `REPAIR`: repair and execution recovery
- `VERIFY`: numerical verification and credibility assessment

Atomic cases score one capability. Integrated workflow cases measure the complete workflow and
are reported separately. Public case material and private evaluator specifications use separate
directories so a release can publish prompts and artifacts without exposing gold answers.

## Quick start

```bash
uv sync --extra dev

uv run moose-benchmark validate benchmark/manifest.yaml
uv run moose-benchmark score \
  --manifest benchmark/manifest.yaml \
  --case-id DIAG-THERMAL-SCHEMA-001 \
  --submission benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001.json \
  --external-gates external-gates.json \
  --output benchmark-results/diag-thermal-schema-001.json

uv run moose-benchmark aggregate \
  --manifest benchmark/manifest.yaml \
  benchmark-results/*.json
uv run pytest -q
```

The external gate file represents evaluator-measured telemetry, not a participant claim. The
example is a static diagnosis case, so CI does not need a MOOSE executable. A separate
integration job can run `ci/moose_smoke.sh` on a runner that defines `MOOSE_APP`.

External gate records are bound to the benchmark version, case ID, and canonical submission hash.
Submitted artifacts are resolved inside the submission workspace and rehashed before scoring.

## Repository layout

```text
benchmark/
  manifest.yaml                 Case registry and benchmark version
  public/cases/<case-id>/       Prompt, starting artifacts, and visible evidence
  private/cases/<case-id>/      Gold criteria and hard-gate definitions
  example-submissions/          Development-only reference answers
templates/
  atomic-case/                  Copy-ready atomic case contract
  integrated-workflow-case/    Copy-ready end-to-end case contract
  submission/                   Standard answer envelope
src/moose_benchmark/
  contracts.py                  Typed public, private, and submission contracts
  loader.py                     Safe case and manifest loading
  comparison.py                 Deterministic criterion comparators
  evaluators/                   Pluggable evaluator interface and starter evaluator
  scoring.py                    Gated case score and suite aggregation
  runner.py                     Bounded, shell-free MOOSE command runner
  cli.py                        Validate, score, aggregate, and run-check commands
tests/                           Contract, scoring, aggregation, and security tests
ci/                              Optional real-MOOSE smoke test
docs/implementation-plan.md      Incremental implementation and release plan
```

## Scoring contract

For atomic case `i`:

```text
raw_score      = 0.70 * capability + 0.20 * evidence + 0.10 * contract
official_score = raw_score when every hard gate passes, otherwise 0
case_pass      = gates_pass and capability >= 80 and raw_score >= 80
```

The Atomic Capability Score is the macro-average of the represented F1 through V4
subcategory means. Production reports should show missing subcategories rather than imply
that a partial development set covers the full benchmark.

## Adding a case

1. Copy `templates/atomic-case` or `templates/integrated-workflow-case`.
2. Choose a stable case ID and `base_problem_id`.
3. Put participant-visible files under `benchmark/public/cases/<case-id>`.
4. Put gold criteria and external gate declarations under
   `benchmark/private/cases/<case-id>`.
5. Register both paths in `benchmark/manifest.yaml`.
6. Add a gold submission and at least one incorrect mutant submission.
7. Run `moose-benchmark validate` and the test suite.

The starter keeps private files in the same repository for convenience. A public benchmark
release should build the participant bundle from `benchmark/public` and retain
`benchmark/private` in a protected evaluator repository or service.

## GitHub

The repository includes `.github/workflows/ci.yml`. After creating an empty GitHub repository:

```bash
git remote add origin git@github.com:YOUR-ACCOUNT/moose-agent-benchmark.git
git push -u origin main
```
