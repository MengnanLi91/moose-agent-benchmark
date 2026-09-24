disp = 0.5

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 80
    xmin = 0
    xmax = 80
  []
[]

[GlobalParams]
  PorousFlowDictator = dictator
  gravity = '0 0 0'
[]

[Variables]
  [porepressure]
    initial_condition = 1e5
  []
  [C]
    initial_condition = 0
  []
[]

[AuxVariables]
  [Darcy_vel_x]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  [Darcy_vel_x]
    type = PorousFlowDarcyVelocityComponent
    variable = Darcy_vel_x
    component = x
    fluid_phase = 0
  []
[]

[UserObjects]
  [dictator]
    type = PorousFlowDictator
    porous_flow_vars = 'porepressure'
    number_fluid_phases = 1
    number_fluid_components = 2
  []
[]

[Kernels]
  [mass_der_water]
    type = PorousFlowMassTimeDerivative
    fluid_component = 1
    variable = porepressure
  []
  [adv_pp]
    type = PorousFlowFullySaturatedDarcyFlow
    variable = porepressure
    fluid_component = 1
  []
  [diff_pp]
    type = PorousFlowDispersiveFlux
    fluid_component = 1
    variable = porepressure
    disp_trans = 0
    disp_long = ${disp}
  []
  [mass_der_C]
    type = PorousFlowMassTimeDerivative
    fluid_component = 0
    variable = C
  []
  [adv_C]
    type = PorousFlowFullySaturatedDarcyFlow
    fluid_component = 0
    variable = C
  []
  [diff_C]
    type = PorousFlowDispersiveFlux
    fluid_component = 0
    variable = C
    disp_trans = 0
    disp_long = ${disp}
  []
[]

[FluidProperties]
  [water]
    type = Water97FluidProperties
  []
[]

[Materials]
  [ps]
    type = PorousFlow1PhaseFullySaturated
    porepressure = porepressure
  []
  [porosity]
    type = PorousFlowPorosityConst
    porosity = 0.25
  []
  [permeability]
    type = PorousFlowPermeabilityConst
    permeability = '2e-12 0 0   0 2e-12 0   0 0 2e-12'
  []
  [water]
    type = PorousFlowSingleComponentFluid
    fp = water
    phase = 0
  []
  [massfrac]
    type = PorousFlowMassFraction
    mass_fraction_vars = C
  []
  [temperature]
    type = PorousFlowTemperature
    temperature = 293
  []
  [diff]
    type = PorousFlowDiffusivityConst
    diffusion_coeff = '0 0'
    tortuosity = 0.1
  []
  [relperm]
    type = PorousFlowRelativePermeabilityConst
    kr = 1
    phase = 0
  []
[]

[BCs]
  [constant_inlet_pressure]
    type = DirichletBC
    variable = porepressure
    value = 1.2e5
    boundary = left
  []
  [constant_outlet_porepressure]
    type = DirichletBC
    variable = porepressure
    value = 1e5
    boundary = right
  []
  [inlet_tracer]
    type = DirichletBC
    variable = C
    value = 0.002
    boundary = left
  []
  [outlet_tracer]
    type = PorousFlowOutflowBC
    variable = C
    boundary = right
    mass_fraction_component = 0
  []
[]

[Preconditioning]
  [basic]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -sub_pc_type -sub_pc_factor_shift_type -pc_asm_overlap'
    petsc_options_value = 'asm lu NONZERO 2'
  []
[]

[Executioner]
  type = Transient
  end_time = 86400000
  dtmax = 432000
  nl_rel_tol = 1e-6
  nl_abs_tol = 1e-12
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1000
  []
[]

[Postprocessors]
  [C_midpoint]
    type = PointValue
    variable = C
    point = '40 0 0'
  []
  [Darcy_velocity_midpoint]
    type = PointValue
    variable = Darcy_vel_x
    point = '40 0 0'
  []
[]

[Outputs]
  file_base = f4_porous_solute
  csv = true
[]
