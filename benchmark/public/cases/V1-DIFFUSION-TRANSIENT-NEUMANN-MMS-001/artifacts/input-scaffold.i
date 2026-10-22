# Copy these protected blocks unchanged into artifacts/solution.i.
[Functions]
  [exact]
    type = ParsedFunction
    expression = '2+exp(-2*pi^2*t)*cos(pi*x)*cos(pi*y)'
  []
[]
[Postprocessors]
  [domain_mean]
    type = ElementAverageValue
    variable = u
    execute_on = 'initial timestep_end'
  []
  [u_l2]
    type = ElementL2Error
    variable = u
    function = exact
    execute_on = 'initial timestep_end'
  []
[]
[Outputs]
  csv = true
  file_base = mms
[]
