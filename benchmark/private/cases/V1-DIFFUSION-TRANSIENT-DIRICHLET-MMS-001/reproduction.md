# Reproduction

This derivation case is calibrated through the protected LLM judge. Score the gold and mutant
fixtures with a reviewed private judge configuration:

```bash
uv run moose-benchmark score \
  --manifest benchmark/manifest.yaml \
  --case-id V1-DIFFUSION-TRANSIENT-DIRICHLET-MMS-001 \
  --submission-dir benchmark/example-submissions/V1-DIFFUSION-TRANSIENT-DIRICHLET-MMS-001 \
  --llm-config /path/to/private-llm-config.yaml \
  --include-disabled
```

The case remains disabled until domain review, benchmark-design review, and live judge
calibration are complete.
