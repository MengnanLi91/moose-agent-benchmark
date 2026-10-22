[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 128
  ny = 128
  elem_type = QUAD4
[]

[Variables]
  [u]
    order = FIRST
    family = LAGRANGE
  []
[]

[ICs]
  [initial]
    type = FunctionIC
    variable = u
    function = exact
  []
[]

[Kernels]
  [time]
    type = TimeDerivative
    variable = u
  []
  [diffusion]
    type = Diffusion
    variable = u
  []
[]

[Functions]
  [exact]
    type = ParsedFunction
    expression = '2+exp(-2*pi^2*t)*cos(pi*x)*cos(pi*y)'
  []
[]

[Postprocessors]
  [domain_mean]
    type = ElementAverageValue
    variable = u
    execute_on = 'initial timestep_end'
  []
  [u_l2]
    type = ElementL2Error
    variable = u
    function = exact
    execute_on = 'initial timestep_end'
  []
[]

[Executioner]
  type = Transient
  scheme = implicit-euler
  dt = 0.0125
  end_time = 0.05
  solve_type = NEWTON
  nl_rel_tol = 1e-12
  nl_abs_tol = 1e-12
[]

[Outputs]
  csv = true
  file_base = mms
  console = false
[]
