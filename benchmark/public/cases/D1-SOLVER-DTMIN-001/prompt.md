# D1 Task — Earliest Failure Stage

Inspect the immutable input and ordered solver events. Identify:

1. the earliest workflow stage that fails; and
2. the propagated terminal symptom that ends the run.

Return `response.json` with this shape:

```json
{
  "claim": {
    "failure_stage": "<stable identifier>",
    "terminal_symptom": "<stable identifier>"
  },
  "evidence": [
    {
      "source_id": "solver_events",
      "observation": "<first-failure observation>",
      "interpretation": "<what that observation establishes>"
    },
    {
      "source_id": "solver_events",
      "observation": "<terminal observation>",
      "interpretation": "<why it is downstream of the first failure>"
    }
  ]
}
```

Use separate evidence entries for the first failed stage and the terminal symptom. Do not
repair the input or attribute the first failure to a downstream time-stepper message.
