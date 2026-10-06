[Mesh]
  [line]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 20
  []
[]

[Variables]
  [temperature]
  []
  [concentration]
  []
[]

[Kernels]
  [temperature_diffusion]
    type = Diffusion
    variable = temperature
  []
  [concentration_diffusion]
    type = MatDiffusion
    variable = concentration
    diffusivity = concentration_diffusivity
  []
[]

[Materials]
  [dependent_diffusivity]
    type = ParsedMaterial
    property_name = concentration_diffusivity
    coupled_variables = temperature
    enable_jit = false
    expression = '1.9'
  []
[]

[BCs]
  [temperature_left]
    type = DirichletBC
    variable = temperature
    boundary = left
    value = 300
  []
  [temperature_right]
    type = DirichletBC
    variable = temperature
    boundary = right
    value = 600
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

[Postprocessors]
  [temperature_average]
    type = ElementAverageValue
    variable = temperature
  []
  [concentration_average]
    type = ElementAverageValue
    variable = concentration
  []
  [diffusivity_average]
    type = ElementAverageMaterialProperty
    mat_prop = concentration_diffusivity
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_rel_tol = 1e-12
  nl_abs_tol = 1e-12
[]

[Outputs]
  csv = true
  exodus = false
[]
