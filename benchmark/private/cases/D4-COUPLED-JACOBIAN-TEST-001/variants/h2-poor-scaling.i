[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 4
  xmax = 1
[]

[Variables]
  [temperature]
  []
  [displacement]
  []
[]

[Kernels]
  [thermal_diffusion]
    type = Diffusion
    variable = temperature
  []
  [thermal_source]
    type = BodyForce
    variable = temperature
    value = 1000000
  []
  [thermal_to_mechanics]
    type = CoupledForce
    variable = displacement
    v = temperature
    coef = 1
  []
  [mechanics_diffusion]
    type = Diffusion
    variable = displacement
  []
  [mechanics_source]
    type = BodyForce
    variable = displacement
    value = 1
  []
[]

[BCs]
  [temperature_left]
    type = DirichletBC
    variable = temperature
    boundary = left
    value = 0
  []
  [temperature_right]
    type = DirichletBC
    variable = temperature
    boundary = right
    value = 0
  []
  [displacement_left]
    type = DirichletBC
    variable = displacement
    boundary = left
    value = 0
  []
  [displacement_right]
    type = DirichletBC
    variable = displacement
    boundary = right
    value = 0
  []
[]

[Preconditioning/smp]
  type = SMP
  full = true
[]

[Debug]
  show_var_residual_norms = true
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_max_its = 1
  petsc_options = '-snes_test_jacobian -snes_test_jacobian_view -snes_force_iteration'
[]

[Outputs]
  exodus = false
[]
