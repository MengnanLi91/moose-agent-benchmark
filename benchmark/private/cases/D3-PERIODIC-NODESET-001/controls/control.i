[Mesh]
  [import]
    type = FileMeshGenerator
    file = periodic_mesh_control.e
  []
[]

[Variables/u]
[]

[Kernels]
  [diffusion]
    type = Diffusion
    variable = u
  []
  [time]
    type = TimeDerivative
    variable = u
  []
[]

[BCs/Periodic/x]
  variable = u
  primary = left
  secondary = right
  translation = '1 0 0'
[]

[Executioner]
  type = Transient
  dt = 1
  num_steps = 1
  solve_type = NEWTON
[]

[Outputs]
  exodus = false
[]
