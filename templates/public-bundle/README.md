# MOOSE Agent Benchmark participant bundle

This archive contains participant-visible benchmark material only. It intentionally excludes
private criteria, gold answers, external gate results, and evaluator code.

## Contents

- `manifest.public.yaml`: enabled cases and benchmark version
- `public/cases/<case-id>/`: prompts, starting artifacts, and visible evidence
- `submission-template/answer.json`: submission envelope template

For each assigned case, read its `case.yaml` and prompt, work only within the declared action and
resource boundaries, and return an answer matching the submission template. Submitted artifact
paths must be relative to the submission workspace and their SHA-256 values must match the files.

Scoring is performed by the protected evaluator service, not from this participant bundle.
