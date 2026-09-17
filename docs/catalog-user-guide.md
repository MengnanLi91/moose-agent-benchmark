# Catalog user guide

This guide is for benchmark authors and reviewers who maintain the collaboration catalog
with Obsidian or a normal text editor.

## Prerequisites

- Git
- `uv`
- Obsidian when using the visual catalog interface

Obsidian is optional. Every catalog record is ordinary Markdown and can be edited in any
text editor.

## Open the catalog in Obsidian

1. Clone the repository and pull the latest changes.
2. In Obsidian, choose **Open folder as vault** and select the repository root.
3. Enable the **Bases** core plugin if it is not already enabled.
4. Open `catalog/Benchmark Dashboard.md`.

The dashboard embeds `catalog/benchmark.base`, which provides filtered views by workflow
status, owner, and benchmark track. Track and subcategory pages explain case-design
boundaries.

## Create a case record

1. Copy `catalog/templates/atomic-case-record.md` or
   `catalog/templates/integrated-case-record.md`.
2. Save it as `catalog/cases/<case-id>.md`.
3. Set the frontmatter identity to match the planned or existing `case.yaml`.
4. Describe the public benchmark intent without copying private evaluator answers.
5. Add or update benchmark files under `benchmark/`.

Atomic records use one of the four tracks and one matching subcategory. Integrated workflow
records must use:

```yaml
case_kind: integrated_workflow
track: null
subcategory: null
```

Keep `case_id`, title, kind, track, subcategory, difficulty, base problem, and physics
domains synchronized with the public case contract once that contract exists.

## Frontmatter fields

- `status`, `priority`, and `owner` drive project views.
- `reviewers` lists GitHub usernames or other stable contributor identifiers.
- The two review flags record domain and benchmark-design approval separately.
- `moose_validation_required` states whether completion requires a real MOOSE run.
- `moose_validated` records that required run after its evidence has been reviewed.
- Source and GitHub fields preserve provenance and discussion links.

## Status lifecycle

- `planned`: accepted idea with no implementation requirement.
- `in_progress`: actively being implemented; partial benchmark files are allowed.
- `blocked`: work cannot continue until a documented issue is resolved.
- `review`: implementation artifacts are present and ready for review.
- `complete`: implementation, required validation, and both review concerns are complete.

The validator derives implementation readiness from repository files. Do not add manual
`ci_passing` or file-readiness properties to a record.

## Ownership and review

Cases in `review` or `complete` require an owner. Complete cases also require at least one
reviewer.

Domain review checks governing physics, constitutive relations, boundary and initial
conditions, numerical setup, reference evidence, and scientific credibility.

Benchmark-design review checks capability isolation, taxonomy, grading objectivity,
public/private boundaries, and gold-versus-mutant discrimination. One person may perform
both roles, but both concerns must be addressed.

## Validate changes

Run:

```bash
uv run moose-benchmark catalog validate
uv run moose-benchmark catalog report
uv run moose-benchmark validate benchmark/manifest.yaml
uv run pytest -q
```

Use strict validation before opening a pull request:

```bash
uv run moose-benchmark catalog validate --strict
```

## Synchronize Obsidian edits with Git

Obsidian saves directly into the local repository. Saving a note therefore makes a normal
Git working-tree change, but it does not update GitHub automatically.

```bash
git pull
git status
git diff
git add catalog/ benchmark/
git commit -m "Add D3 thermal diagnosis case"
git push
```

Open a pull request after pushing. The optional Obsidian Git plugin can expose the same Git
operations inside Obsidian, but automated periodic commits are discouraged.

## Public/private information boundary

Catalog records may summarize the benchmark purpose, participant-visible starting state,
required output, permitted actions, provenance, and high-level acceptance conditions.

Do not copy private expected answers, hidden mutants, evaluator-only reasoning, private
tolerances, or unreleased reference outputs into catalog Markdown.

## Troubleshooting

### The catalog validator reports an identity mismatch

Update the catalog frontmatter or public `case.yaml` so the shared identity fields agree.
Physics-domain ordering may differ, but the domain sets must be equal.

### Strict validation reports a missing record

Create one catalog record for every manifest entry and every public case directory.

### Obsidian changes do not appear on GitHub

Check `git status`, then commit and push the local changes. Obsidian does not replace Git
transport.

### A pull creates a Markdown conflict

Resolve the conflict in the catalog file, preserve valid YAML delimiters, and rerun strict
validation before committing the resolution.

### A case cannot be marked complete

Run `catalog report --format json` and inspect `readiness_gaps` for the missing implementation,
review, or MOOSE-validation requirement.
