[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 128
  ny = 128
  elem_type = QUAD4
[]

[Variables]
  [eta]
    order = FIRST
    family = LAGRANGE
  []
[]

[ICs]
  [initial]
    type = FunctionIC
    variable = eta
    function = exact
  []
[]

[Kernels]
  [time]
    type = TimeDerivative
    variable = eta
  []
  [bulk]
    type = AllenCahn
    variable = eta
    f_name = free_energy
  []
  [interface]
    type = SimpleACInterface
    variable = eta
    kappa_name = kappa
  []
  [source]
    type = BodyForce
    variable = eta
    function = forcing
  []
[]

[Materials]
  [properties]
    type = GenericConstantMaterial
    prop_names = 'L kappa'
    prop_values = '1 0.01'
  []
  [energy]
    type = DerivativeParsedMaterial
    property_name = free_energy
    coupled_variables = eta
    expression = 'eta^2*(1-eta)^2'
    derivative_order = 2
  []
[]

[Functions]
  [exact]
    type = ParsedFunction
    expression = '0.5+0.1*exp(-t)*sin(pi*x)*sin(pi*y)'
  []
  [forcing]
    type = ParsedFunction
    expression = '(-2+0.02*pi^2)*(0.1*exp(-t)*sin(pi*x)*sin(pi*y))+4*(0.1*exp(-t)*sin(pi*x)*sin(pi*y))^3'
  []
[]

[BCs]
  [boundary]
    type = FunctionDirichletBC
    variable = eta
    boundary = 'left right top bottom'
    function = exact
  []
[]

[Postprocessors]
  [eta_l2]
    type = ElementL2Error
    variable = eta
    function = exact
  []
[]

[Executioner]
  type = Transient
  scheme = implicit-euler
  dt = 0.1
  end_time = 1
  solve_type = NEWTON
  nl_rel_tol = 1e-11
[]

[Outputs]
  csv = true
  file_base = mms
  console = false
[]
