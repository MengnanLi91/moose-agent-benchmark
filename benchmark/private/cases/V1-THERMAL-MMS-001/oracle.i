[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 128
  ny = 128
  elem_type = QUAD4
[]

[Variables]
  [T]
    order = FIRST
    family = LAGRANGE
  []
[]

[ICs]
  [initial]
    type = FunctionIC
    variable = T
    function = exact
  []
[]

[Kernels]
  [time]
    type = TimeDerivative
    variable = T
  []
  [conduction]
    type = Diffusion
    variable = T
  []
  [source]
    type = BodyForce
    variable = T
    function = forcing
  []
[]

[Functions]
  [exact]
    type = ParsedFunction
    expression = 'exp(-t)*sin(pi*x)*sin(pi*y)'
  []
  [forcing]
    type = ParsedFunction
    expression = '(-1+2*pi^2)*exp(-t)*sin(pi*x)*sin(pi*y)'
  []
[]

[BCs]
  [boundary]
    type = DirichletBC
    variable = T
    boundary = 'left right top bottom'
    value = 0
  []
[]

[Postprocessors]
  [T_l2]
    type = ElementL2Error
    variable = T
    function = exact
  []
[]

[Executioner]
  type = Transient
  scheme = implicit-euler
  dt = 0.1
  end_time = 1
  solve_type = NEWTON
  nl_rel_tol = 1e-12
  nl_abs_tol = 1e-12
[]

[Outputs]
  csv = true
  file_base = mms
  console = false
[]
