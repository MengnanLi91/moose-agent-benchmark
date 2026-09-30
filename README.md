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
  --case-id D1-SOLVER-DTMIN-001 \
  --submission-dir benchmark/example-submissions/D1-SOLVER-DTMIN-001 \
  --output benchmark-results/d1-solver-dtmin-001.json

uv run moose-benchmark aggregate \
  --manifest benchmark/manifest.yaml \
  benchmark-results/*.json
uv run pytest -q
```

To score FORM cases, install the optional judge adapters and provide a private configuration:

```bash
uv sync --extra dev --extra llm
export OPENAI_API_KEY=...
uv run moose-benchmark score \
  --manifest benchmark/manifest.yaml \
  --case-id F2-THERMAL-REFLECTOR-001 \
  --submission-dir benchmark/example-submissions/F2-THERMAL-REFLECTOR-001 \
  --llm-config templates/evaluator/llm-config.yaml
```

The central configuration supports `openai`, `claude`, `litellm`, and `ollama`. LiteLLM uses
its OpenAI-compatible proxy URL; API keys are read from the named environment variable.

## How to read a benchmark case

Each implemented benchmark case has four layers:

1. **Catalog record** — the human-readable purpose, capability boundary, provenance, and
   implementation status under `catalog/cases/<case-id>.md`.
2. **Public case bundle** — everything the evaluated agent may see under
   `benchmark/public/cases/<case-id>/`, including `case.yaml`, the prompt, immutable
   artifacts, and participant-visible evidence.
3. **Private evaluator and reproduction material** — scoring truth, expected claims,
   controls, and validation outputs under `benchmark/private/cases/<case-id>/`.
4. **Example submissions** — gold and deliberately incorrect development fixtures under
   `benchmark/example-submissions/`.

For an unbiased evaluation, provide the agent only the public case bundle. Do not expose
private evaluator material or example submissions. The example submissions are intended to
test scoring behavior and are not held-out benchmark answers.

When reviewing a case, read the catalog record first, then `case.yaml`, `prompt.md`, and the
public artifacts and evidence. Benchmark maintainers can then inspect the private evaluator
and reproduction material to understand scoring and provenance.

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

### 3. Install the Obsidian Git community plugin

1. Open **Settings → Community plugins** and enable community plugins if prompted.
2. Select **Browse**, search for **Git**, then choose **Install** and **Enable**.
3. Confirm that the repository's Git remote and GitHub authentication already work from the
   command line. The plugin uses the Git configuration and credentials on your computer.

The plugin adds Git commands to Obsidian's command palette and may also provide a source
control view for reviewing changed files.

### 4. View the examples

Open a record from the dashboard or browse `catalog/cases/` directly. For example:

- `catalog/cases/F1-THERMAL-RADIATION-001.md` is a planned formulation case.
- `catalog/cases/F1-SOLID-DUCT-BOWING-001.md` is an implemented physics-specification case.
- `catalog/cases/F2-THERMAL-REFLECTOR-001.md` is an implemented weak-form case.
- `catalog/cases/F3-PHASEFIELD-SPLITCH-001.md` is an implemented object-mapping case.
- `catalog/cases/F4-POROUS-SOLUTE-001.md` is an implemented input-assembly case.
- `catalog/cases/R3-FLUID-PRESSURE-NULLSPACE-001.md` is a planned repair case.
- `catalog/cases/D1-SOLVER-DTMIN-001.md` documents an implemented diagnostic case.

Each record has YAML frontmatter for searchable project metadata followed by Markdown
sections describing the benchmark purpose, starting information, required output, capability
isolation, provenance, and implementation checklist.

Most seed examples have `status: planned`. They are benchmark designs, not runnable bundles
yet. Runnable cases also require public artifacts, a private evaluator, development
submissions, and a manifest entry under `benchmark/`.

### 5. Edit, commit, and push from Obsidian

Before editing, open the command palette with **Ctrl/Cmd+P** and run the Git plugin's
**Pull** command to retrieve remote changes.

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

After editing:

1. Save the file and review the changed files in the Git source control view.
2. Run the repository validation commands below.
3. From **Ctrl/Cmd+P**, run the Git plugin's **Commit all changes** command and enter a clear
   commit message.
4. Run the Git plugin's **Push** command to push the commit to GitHub.

For shared branches, pull before editing and confirm that you are on the intended branch
before committing or pushing.

### 6. Validate and review the changes

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

The Obsidian Git community plugin can commit and push directly from the vault. Pull requests
remain recommended when branch protection or review is required.

See the [catalog user guide](docs/catalog-user-guide.md) for authoring and review instructions
and the [catalog developer guide](docs/catalog-developer-guide.md) for implementation details.

Runner-owned `run-record.json` files contain model identity, measured usage, response hashes,
and artifact hashes. Participants return only the requested response and files. External gate
records represent protected evaluator measurements rather than participant claims.

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
  submission/                   Participant response template
  evaluator/                    Private run-record and LLM configuration templates
src/moose_benchmark/
  contracts.py                  Typed public, private, and submission contracts
  loader.py                     Safe case and manifest loading
  comparison.py                 Deterministic criterion comparators
  evaluators/                   Pluggable evaluator interface and starter evaluator
  llm/                          OpenAI, Claude, LiteLLM-proxy, and Ollama judge adapters
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

FORM cases use capability-only scoring:

```text
raw_score      = capability
official_score = raw_score when every hard gate passes, otherwise 0
case_pass      = gates_pass and capability >= 80
```

Transitional structured DIAG and integrated cases retain the `0.70/0.20/0.10` balanced profile.
Submission integrity, required artifacts, and resource budgets are hard gates rather than FORM
score components.

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
6. Add gold and mutant submission directories with runner-owned records.
7. Run `moose-benchmark validate` and the test suite.

The starter keeps private files in the same repository for convenience. A public benchmark
release should build the participant bundle from `benchmark/public` and retain
`benchmark/private` in a protected evaluator repository or service.
