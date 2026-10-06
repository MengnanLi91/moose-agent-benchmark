rho = 1
mu = 1
n = 4

[Mesh]
  [generated]
    type = DistributedRectilinearMeshGenerator
    dim = 2
    xmin = 0
    xmax = 1
    ymin = 0
    ymax = 1
    nx = ${n}
    ny = ${n}
    elem_type = QUAD4
  []
  second_order = true
  parallel_type = distributed
[]

[Variables]
  [velocity]
    order = SECOND
    family = LAGRANGE_VEC
  []
  [pressure]
    order = FIRST
    family = LAGRANGE
  []
  [concentration]
    order = FIRST
    family = LAGRANGE
  []
[]

[Kernels]
  [mass]
    type = INSADMass
    variable = pressure
  []
  [mass_matrix]
    type = MassMatrix
    variable = pressure
    matrix_tags = mass
  []
  [pressure_stabilization]
    type = Reaction
    variable = pressure
  []
  [viscous]
    type = INSADMomentumViscous
    variable = velocity
  []
  [pressure_gradient]
    type = INSADMomentumPressure
    variable = velocity
    pressure = pressure
    integrate_p_by_parts = true
  []
  [concentration_diffusion]
    type = Diffusion
    variable = concentration
  []
  [concentration_transport]
    type = ADConservativeAdvection
    variable = concentration
    velocity_variable = velocity
  []
[]

[BCs]
  [no_slip]
    type = ADVectorFunctionDirichletBC
    variable = velocity
    boundary = 'bottom right left'
  []
  [lid]
    type = ADVectorFunctionDirichletBC
    variable = velocity
    boundary = top
    function_x = 1
  []
  [concentration_left]
    type = DirichletBC
    variable = concentration
    boundary = left
    value = 1
  []
  [concentration_right]
    type = DirichletBC
    variable = concentration
    boundary = right
    value = 0
  []
[]

[Materials]
  [fluid]
    type = ADGenericConstantMaterial
    prop_names = 'rho mu'
    prop_values = '${rho} ${mu}'
  []
  [ins]
    type = INSADMaterial
    velocity = velocity
    pressure = pressure
  []
[]

[Problem]
  type = NavierStokesProblem
  mass_matrix = mass
  extra_tag_matrices = mass
  set_schur_pre = mass
[]

[Preconditioning]
  [FSP]
    type = FSP
    topsplit = system
    [system]
      vars = 'velocity pressure concentration'
      splitting = 'fluid concentration'
      splitting_type = additive
    []
    [fluid]
      splitting = 'velocity pressure'
      splitting_type = additive
    []
    [velocity]
      vars = velocity
      petsc_options_iname = '-pc_type -ksp_type'
      petsc_options_value = 'jacobi preonly'
    []
    [pressure]
      vars = pressure
      petsc_options_iname = '-pc_type -ksp_type'
      petsc_options_value = 'jacobi preonly'
    []
    [concentration]
      vars = concentration
      petsc_options_iname = '-pc_type -ksp_type'
      petsc_options_value = 'jacobi preonly'
    []
  []
[]

[Postprocessors]
  [pressure_average]
    type = ElementAverageValue
    variable = pressure
  []
  [concentration_average]
    type = ElementAverageValue
    variable = concentration
  []
[]

[Correctors]
  [pin_pressure]
    type = NSPressurePin
    pin_type = average
    variable = pressure
    pressure_average = pressure_average
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_rel_tol = 1e-10
  nl_abs_tol = 1e-12
  nl_max_its = 20
  l_tol = 1e-8
  l_max_its = 200
[]

[Outputs]
  exodus = false
  csv = true
  print_linear_residuals = false
[]
