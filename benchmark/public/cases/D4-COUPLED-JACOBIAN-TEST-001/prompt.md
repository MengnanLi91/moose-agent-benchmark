# D4 Task — Choose the Discriminating Next Test

Read the coupled-model summary and diagnostic context. Select exactly one next action from
the supplied stable action IDs. The action should maximally distinguish:

- **H1:** a missing off-diagonal coupling contribution; and
- **H2:** a consistent Jacobian with residual-scale imbalance.

Return:

- `claim.next_action`: one supplied action ID;
- `claim.information_gain`: a set of concepts describing what the action resolves;
- `claim.predictions.H1`: the expected H1 signature; and
- `claim.predictions.H2`: the expected H2 signature.

Use these prediction keys:

```json
{
  "H1": {"jacobian_comparison": "<signature>"},
  "H2": {
    "jacobian_comparison": "<signature>",
    "remaining_issue": "<signature>"
  }
}
```

Include one artifact-bound evidence entry citing `diagnostic_context`. Do not repair the
model or choose iteration, preconditioner, timestep, or mesh tuning merely to seek progress.
