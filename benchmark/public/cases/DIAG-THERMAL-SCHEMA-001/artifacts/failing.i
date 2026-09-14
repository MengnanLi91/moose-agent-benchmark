[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 8
[]

[Variables]
  [u]
  []
[]

[Kernels]
  [diffusion]
    type = NotARegisteredKernel
    variable = u
  []
[]

[BCs]
  [left]
    type = DirichletBC
    variable = u
    boundary = left
    value = 0
  []
  [right]
    type = DirichletBC
    variable = u
    boundary = right
    value = 1
  []
[]

[Executioner]
  type = Steady
[]
