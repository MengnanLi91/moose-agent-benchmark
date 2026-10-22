# Variable-permeability PorousFlow manufactured-solution candidate.

[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 8
  ny = 8
  elem_type = QUAD4
[]

[GlobalParams]
  PorousFlowDictator = dictator
  gravity = '0 0 0'
[]

[Variables]
  [p]
    order = FIRST
    family = LAGRANGE
  []
[]

[AuxVariables]
  [permeability_value]
    order = FIRST
    family = LAGRANGE
  []
[]

[AuxKernels]
  [permeability]
    type = FunctionAux
    variable = permeability_value
    function = permeability
    execute_on = initial
  []
[]

[Kernels]
  [darcy]
    type = PorousFlowFullySaturatedDarcyFlow
    variable = p
    fluid_component = 0
  []
  [source]
    type = BodyForce
    variable = p
    function = forcing
  []
[]

[UserObjects]
  [dictator]
    type = PorousFlowDictator
    porous_flow_vars = p
    number_fluid_phases = 1
    number_fluid_components = 1
  []
[]

[FluidProperties]
  [fluid]
    type = SimpleFluidProperties
    density0 = 1
    viscosity = 1
    bulk_modulus = 1e30
    thermal_expansion = 0
  []
[]

[Materials]
  [temperature]
    type = PorousFlowTemperature
  []
  [pressure]
    type = PorousFlow1PhaseFullySaturated
    porepressure = p
  []
  [mass_fraction]
    type = PorousFlowMassFraction
  []
  [fluid_material]
    type = PorousFlowSingleComponentFluid
    fp = fluid
    phase = 0
  []
  [porosity]
    type = PorousFlowPorosity
    porosity_zero = 1
  []
  [permeability]
    type = PorousFlowPermeabilityTensorFromVar
    perm = permeability_value
    k_anisotropy = '1 0 0 0 1 0 0 0 1'
  []
[]

[Functions]
  [exact]
    type = ParsedFunction
    expression = '1+sin(pi*x)*sin(pi*y)'
  []
  [permeability]
    type = ParsedFunction
    expression = '1+x/4'
  []
  [forcing]
    type = ParsedFunction
    expression = '2*pi^2*(1+x/4)*sin(pi*x)*sin(pi*y)-pi*cos(pi*x)*sin(pi*y)/4'
  []
  [wrong_boundary]
    type = ParsedFunction
    expression = '0'
  []
[]

[BCs]
  [boundary]
    type = FunctionDirichletBC
    variable = p
    boundary = 'left right top bottom'
    function = wrong_boundary
  []
[]

[Postprocessors]
  [p_l2]
    type = ElementL2Error
    variable = p
    function = exact
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
  nl_rel_tol = 1e-12
[]

[Outputs]
  csv = true
  file_base = mms
[]
