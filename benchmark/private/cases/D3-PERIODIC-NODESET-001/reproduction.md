# D3 reproduction and control

Validated on September 29, 2026 with MOOSE commit
`c2dfd9fedd3193740a5278ec32269450c618e3b7`, PETSc `3.25.2`,
`modules/combined/combined-opt`, and one MPI process.

Regenerate the faulty and control meshes from `controls/`:

```bash
"$MOOSE_APP" -i make-faulty-mesh.i --mesh-only periodic_mesh.e
"$MOOSE_APP" -i make-control-mesh.i --mesh-only periodic_mesh_control.e
```

Run the public faulty input from its artifact directory:

```bash
"$MOOSE_APP" -i failing.i
```

Run the sideset-based control from `controls/`:

```bash
"$MOOSE_APP" -i control.i
```

The faulty run must emit the boundary-match warning and establish no constrained DOFs. The
control must report `left <-> right`, establish five constrained DOFs, and emit no match
warning.
