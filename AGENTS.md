# Repository instructions

Favor clarity, small diffs, and incremental improvements. Start with the simplest working
solution, verify it, and add complexity only when needed.

Do not add pylint pragmas or configure pylint.

## Tooling

- Environment and runner: `uv`
- Formatter: Black
- Linter and import sorting: Ruff
- Tests: pytest

When `pyproject.toml` changes, run:

```bash
uv sync --extra dev
```

Before committing, run:

```bash
uv run black --check .
uv run ruff check .
uv run pytest -q
```

If a `.codegraph/` index is present, use CodeGraph before grep or direct file inspection when
locating or understanding code. Do not create an index automatically.
