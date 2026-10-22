# Copy these protected blocks unchanged into artifacts/solution.i.
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
    function = exact_u
  []
  [v_l2]
    type = ElementL2Error
    variable = v
    function = exact_v
  []
  [p_l2]
    type = ElementL2Error
    variable = p
    function = exact_p
  []
[]
[Outputs]
  csv = true
  file_base = mms
[]
