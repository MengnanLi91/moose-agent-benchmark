# MOOSE Agent Benchmark

This repository is a runnable starting point for evaluating MOOSE agents across four
separate capabilities:

- `FORM`: physics-to-MOOSE formulation
- `DIAG`: MOOSE-native error analysis
- `REPAIR`: repair and execution recovery
- `VERIFY`: numerical verification and credibility assessment

Atomic cases score one capability. Integrated workflow cases measure the complete workflow and
are reported separately. Public case material and private evaluator specifications use separate
directories so a release can publish prompts and artifacts without exposing gold answers.

## Quick start: run the benchmark

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

## Quick start: view and edit examples in Obsidian

The catalog is a collection of ordinary Markdown files, so the repository can be opened
directly as an Obsidian vault. Obsidian is optional, but its Bases view provides a convenient
dashboard for browsing cases by track, subcategory, status, owner, and difficulty.

### 1. Install the project

Install Git, `uv`, and the Obsidian desktop application. Then clone the repository and create
the development environment:

```bash
git clone https://github.com/MengnanLi91/moose-agent-benchmark.git
cd moose-agent-benchmark
uv sync --extra dev
```

Confirm that the catalog is valid:

```bash
uv run moose-benchmark catalog validate --strict
uv run moose-benchmark catalog report
```

### 2. Open the catalog in Obsidian

1. Start Obsidian and choose **Open folder as vault**.
2. Select the cloned `moose-agent-benchmark` repository root, not only the `catalog/`
   directory.
3. Open **Settings → Core plugins** and enable **Bases**.
4. Open `catalog/Benchmark Dashboard.md`.

The dashboard embeds `catalog/benchmark.base`. Use its tables to browse all cases or filter
them by FORM, DIAG, REPAIR, and VERIFY.

### 3. View the examples

Open a record from the dashboard or browse `catalog/cases/` directly. For example:

- `catalog/cases/F1-THERMAL-RADIATION-001.md` is a planned formulation case.
- `catalog/cases/R3-FLUID-PRESSURE-NULLSPACE-001.md` is a planned repair case.
- `catalog/cases/DIAG-THERMAL-SCHEMA-001.md` documents the implemented example case.

Each record has YAML frontmatter for searchable project metadata followed by Markdown
sections describing the benchmark purpose, starting information, required output, capability
isolation, provenance, and implementation checklist.

Most seed examples have `status: planned`. They are benchmark designs, not runnable bundles
yet. Runnable cases also require public artifacts, a private evaluator, development
submissions, and a manifest entry under `benchmark/`.

### 4. Edit an example

Open a planned record and update its frontmatter and Markdown body. Common first edits include:

- assigning `owner`;
- changing `status` from `planned` to `in_progress`;
- refining the starting information and required output;
- documenting the base model, evidence, and provenance;
- checking completed implementation tasks.

Obsidian saves changes directly to the repository. To create a separate case instead of
editing an existing example, copy `catalog/templates/atomic-case-record.md` or
`catalog/templates/integrated-case-record.md` into `catalog/cases/<case-id>.md`.

Keep private expected answers, hidden mutations, evaluator reasoning, and unreleased numeric
tolerances out of catalog records.

### 5. Validate and review the changes

Run the catalog, benchmark, and test checks:

```bash
uv run moose-benchmark catalog validate --strict
uv run moose-benchmark catalog report
uv run moose-benchmark validate benchmark/manifest.yaml
uv run pytest -q
```

Then inspect the files that Obsidian changed:

```bash
git status
git diff
```

Obsidian does not push changes to GitHub automatically. The Obsidian Git community plugin is
optional; normal Git commits and pull requests remain the recommended collaboration workflow.

See the [catalog user guide](docs/catalog-user-guide.md) for authoring and review instructions
and the [catalog developer guide](docs/catalog-developer-guide.md) for implementation details.

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
catalog/
  Benchmark Dashboard.md        Obsidian entry point
  benchmark.base                Filtered case-development views
  cases/                        Human-facing case records
  templates/                    Atomic and integrated record templates
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
docs/catalog-user-guide.md       Catalog author and reviewer workflow
docs/catalog-developer-guide.md  Catalog architecture and extension guide
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
