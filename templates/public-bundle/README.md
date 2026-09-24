# MOOSE Agent Benchmark participant bundle

This archive contains participant-visible benchmark material only. It intentionally excludes
private criteria, gold answers, external gate results, and evaluator code.

## Contents

- `manifest.public.yaml`: enabled cases and benchmark version
- `public/cases/<case-id>/`: prompts, starting artifacts, and visible evidence
- `submission-template/response.md`: free-response template

For each assigned case, read its `case.yaml` and prompt, work only within the declared action and
resource boundaries, and return natural Markdown plus any specifically requested files. Do not
provide case identity, source IDs, hashes, timing, model identity, or usage telemetry; the runner
records that metadata after generation.

Scoring is performed by the protected evaluator service, not from this participant bundle.
