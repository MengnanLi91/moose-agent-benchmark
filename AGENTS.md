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

## Markdown and math

- Use MathJax-style delimiters in Markdown: `$...$` for inline math and `$$...$$` for
  display math.
- Do not use LaTeX parenthesis or bracket math delimiters.
- Leave a blank line before and after each `$$` display block.
- Do not place display equations inside fenced code blocks.
- In Markdown tables, use inline math because multiline display equations render poorly.
- In list items, put display equations on their own lines and indent only when necessary.
- Prefer standard MathJax commands such as `\mathbf`, `\boldsymbol`, `\frac`, `\nabla`, and
  `\partial`.
