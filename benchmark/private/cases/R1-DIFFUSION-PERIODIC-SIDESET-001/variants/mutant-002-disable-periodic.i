[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 2
    xmin = 0
    xmax = 2
    ymin = 0
    ymax = 2
    nx = 8
    ny = 8
  []
  [mark_removed]
    type = SubdomainBoundingBoxGenerator
    input = base
    block_id = 1
    bottom_left = '0 1 0'
    top_right = '1 2 0'
  []
  [l_shape]
    type = BlockDeletionGenerator
    input = mark_removed
    block = 1
  []
  [right_periodic]
    type = ParsedGenerateSideset
    input = l_shape
    included_boundaries = right
    combinatorial_geometry = 'y < 1.000001'
    new_sideset_name = right_periodic
    enable_jit = false
  []
[]

[Variables]
  [u]
  []
[]

[Kernels]
  [diffusion]
    type = Diffusion
    variable = u
  []
  [source]
    type = BodyForce
    variable = u
    value = 1
  []
[]

[BCs]
  [periodic_replacement]
    type = DirichletBC
    variable = u
    boundary = 'left right_periodic'
    value = 0
  []
  [bottom]
    type = DirichletBC
    variable = u
    boundary = bottom
    value = 0
  []
[]

[Postprocessors]
  [left_value]
    type = PointValue
    variable = u
    point = '0 0.5 0'
  []
  [right_value]
    type = PointValue
    variable = u
    point = '2 0.5 0'
  []
  [solution_average]
    type = ElementAverageValue
    variable = u
  []
  [solution_integral]
    type = ElementIntegralVariablePostprocessor
    variable = u
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_rel_tol = 1e-10
  nl_abs_tol = 1e-12
  l_tol = 1e-12
[]

[Outputs]
  exodus = false
  csv = true
[]
