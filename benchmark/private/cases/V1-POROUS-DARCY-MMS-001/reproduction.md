# Reproduction

Run the private canonical input with MOOSE revision
`c2dfd9fedd3193740a5278ec32269450c618e3b7` and executable hash
`3be083e88c63c265e1c98a3f0cbd401fb2d7feb39547c6fa22ff1cb2f4f34472`:

```bash
uv run moose-benchmark generate-mms-reference \
  --manifest benchmark/manifest.yaml \
  --case-id V1-POROUS-DARCY-MMS-001 \
  --moose-dir /path/to/moose \
  --executable /path/to/moose/modules/combined/combined-opt \
  --output benchmark/private/cases/V1-POROUS-DARCY-MMS-001/reference/metrics.json \
  --validation-dir benchmark/private/cases/V1-POROUS-DARCY-MMS-001/validation
```

The command leaves frozen metrics unchanged when they match and fails on drift. Use
`--update-reference` only after reviewing and accepting an intentional baseline change. The case
remains disabled until domain and benchmark-design reviews are complete.
