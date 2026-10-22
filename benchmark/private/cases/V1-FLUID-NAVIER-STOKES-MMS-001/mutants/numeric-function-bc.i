# Taylor-Hood incompressible Navier-Stokes manufactured-solution candidate.

[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 4
  ny = 4
  elem_type = QUAD9
[]

[GlobalParams]
  gravity = '0 0 0'
[]

[Variables]
  [u]
    order = SECOND
    family = LAGRANGE
  []
  [v]
    order = SECOND
    family = LAGRANGE
  []
  [p]
    order = FIRST
    family = LAGRANGE
  []
  [lambda]
    order = FIRST
    family = SCALAR
  []
[]

[AuxVariables]
  [divergence]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  [divergence]
    type = DivergenceAux
    variable = divergence
    u = u
    v = v
  []
[]

[Kernels]
  [mass]
    type = INSMass
    variable = p
    u = u
    v = v
    pressure = p
  []
  [momentum_x]
    type = INSMomentumLaplaceForm
    variable = u
    u = u
    v = v
    pressure = p
    component = 0
  []
  [momentum_y]
    type = INSMomentumLaplaceForm
    variable = v
    u = u
    v = v
    pressure = p
    component = 1
  []
  [force_x]
    type = BodyForce
    variable = u
    function = force_x
  []
  [force_y]
    type = BodyForce
    variable = v
    function = force_y
  []
  [pressure_multiplier]
    type = ScalarLagrangeMultiplier
    variable = p
    lambda = lambda
  []
[]

[Functions]
  [exact_u]
    type = ParsedFunction
    expression = 'sin(pi*x)*cos(pi*y)'
  []
  [exact_v]
    type = ParsedFunction
    expression = '-cos(pi*x)*sin(pi*y)'
  []
  [exact_p]
    type = ParsedFunction
    expression = 'cos(2*pi*x)+cos(2*pi*y)'
  []
  [force_x]
    type = ParsedFunction
    expression = '2*pi^2*sin(pi*x)*cos(pi*y)-1.5*pi*sin(2*pi*x)'
  []
  [force_y]
    type = ParsedFunction
    expression = '-2*pi^2*cos(pi*x)*sin(pi*y)-1.5*pi*sin(2*pi*y)'
  []
[]

[ScalarKernels]
  [pressure_constraint]
    type = AverageValueConstraint
    variable = lambda
    pp_name = pressure_integral
    value = 0
  []
[]

[BCs]
  [u_boundary]
    type = DirichletBC
    variable = u
    boundary = 'left right top bottom'
    value = exact_u
  []
  [v_boundary]
    type = DirichletBC
    variable = v
    boundary = 'left right top bottom'
    value = exact_v
  []
[]

[Materials]
  [fluid]
    type = GenericConstantMaterial
    prop_names = 'rho mu'
    prop_values = '1 1'
  []
[]

[Postprocessors]
  [pressure_integral]
    type = ElementIntegralVariablePostprocessor
    variable = p
    execute_on = linear
  []
  [u_l2]
    type = ElementL2Error
    variable = u
    value = exact_u
  []
  [v_l2]
    type = ElementL2Error
    variable = v
    value = exact_v
  []
  [p_l2]
    type = ElementL2Error
    variable = p
    function = exact_p
  []
  [divergence_l2]
    type = ElementL2Norm
    variable = divergence
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_rel_tol = 1e-11
  l_tol = 1e-12
  l_max_its = 500
[]

[Outputs]
  csv = true
  file_base = mms
[]
