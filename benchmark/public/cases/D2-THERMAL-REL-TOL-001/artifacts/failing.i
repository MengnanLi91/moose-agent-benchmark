[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 20
  xmax = 1
[]

[Variables/temperature]
[]

[Kernels]
  [conduction]
    type = Diffusion
    variable = temperature
  []
  [heat_source]
    type = BodyForce
    variable = temperature
    value = 1e-6
  []
[]

[BCs]
  [left]
    type = DirichletBC
    variable = temperature
    boundary = left
    value = 0
  []
  [right]
    type = DirichletBC
    variable = temperature
    boundary = right
    value = 0
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_rel_tol = 1e-6
  nl_abs_tol = 1e-12
  nl_max_its = 1
  petsc_options = '-ksp_converged_reason'
  petsc_options_iname = '-ksp_rtol -ksp_max_it -pc_type'
  petsc_options_value = '0.99      1           none'
[]

[Outputs]
  exodus = false
[]
