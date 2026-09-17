# Catalog developer guide

This guide describes the catalog subsystem for maintainers extending its Python models,
validation, reports, or Obsidian views.

## Architecture

The collaboration layer extends the existing package rather than creating a separate
application:

```text
catalog/cases/*.md
        |
        v
moose_benchmark.catalog.loader
        |
        v
models -> validator -> report
        |
        v
moose-benchmark catalog ...
```

`case.yaml` remains authoritative for participant-facing executable metadata. Private
evaluation files remain authoritative for gold criteria and gates. Catalog Markdown owns
workflow state, ownership, review state, provenance summaries, and human-readable design
notes.

The catalog validator compares only shared identity fields. It must not copy project state
into `case.yaml` or private evaluator data into Markdown.

## Parsing and models

`catalog/loader.py` recognizes a Markdown document only when its first line and closing
frontmatter delimiter are `---`. It uses `yaml.safe_load` and preserves the remaining
Markdown body.

`CatalogRecord` inherits the repository's strict Pydantic model behavior, so unknown
frontmatter fields fail validation. It reuses `CaseKind`, `Track`, `Difficulty`,
`AtomicSubcategory`, and `TRACK_SUBCATEGORIES` from the executable contracts.

Integrated records use the existing machine convention:

```yaml
case_kind: integrated_workflow
track: null
subcategory: null
```

`CoverageConfig` requires all four tracks and difficulty levels, positive targets, and equal
track/difficulty totals. Changing the release target therefore requires editing configuration,
not Python constants.

## Validation flow

Normal validation loads every catalog record, validates its filename and schema, and checks
machine files when they exist. Manifest paths take precedence; unregistered work uses the
standard public and private case paths.

Strict validation additionally requires a catalog record for every manifest entry and public
case directory. CI uses strict mode.

Shared identity comparisons are exact except for `physics_domains`, which is compared as a
set. Public contracts, private evaluations, gold fixtures, and mutant fixtures must parse
through their existing typed loaders.

## Readiness policy

Implementation readiness is derived from:

- valid public contract,
- valid private evaluation,
- manifest registration,
- valid `<case-id>.json` development submission,
- at least one valid `<case-id>-mutant*.json` submission.

`review` requires implementation readiness and an owner. `complete` additionally requires a
reviewer, domain review, benchmark-design review, and any declared MOOSE validation.

Readiness is never written back to Markdown. CI success is evidence produced by CI rather
than a persistent frontmatter field.

## CLI contracts

```bash
moose-benchmark catalog validate [--strict] [--repo-root PATH]
moose-benchmark catalog report [--format text|json] [--output PATH] [--repo-root PATH]
```

Both commands default to the current directory as the repository root. Validation prints all
discovered errors before returning a nonzero exit status. Reporting first performs normal
validation and refuses to summarize an invalid catalog.

The JSON report contains stable top-level keys for release metadata, totals, status counts,
track counts, subcategory counts, difficulty counts, physics-domain counts, integrated-case
counts, owner/review queues, and readiness gaps.

Target progress applies only to atomic cases. Status totals include both atomic and integrated
records. For each grouping, `cataloged`, `implemented`, and `complete` remain separate so a
planned case cannot be mistaken for a runnable case.

## Testing

Keep catalog tests in flat `tests/test_catalog_*.py` files to match the repository. Cover
frontmatter parsing, model shape, identity consistency, status policy, strict coverage,
reports, and CLI exit behavior.

Before committing, run:

```bash
uv run moose-benchmark catalog validate --strict
uv run moose-benchmark validate benchmark/manifest.yaml
uv run black --check .
uv run ruff check .
uv run pytest -q
```

## Schema evolution

Add new optional fields with defaults when possible. A breaking required-field or semantic
change requires a new `catalog_schema_version`, explicit compatibility handling, updated
templates, and migration of all tracked records.

Do not silently accept unknown properties or reinterpret existing status values.

## Obsidian Base verification

Obsidian is not a CI dependency. After changing `benchmark.base`, open the repository root as
a vault, enable Bases, and verify that:

1. only `catalog/cases` records appear,
2. workflow and track filters return the expected records,
3. columns display frontmatter properties,
4. links from dashboard, track, and subcategory pages resolve.

Keep `.obsidian/` ignored because it contains user-specific plugin and workspace state.
