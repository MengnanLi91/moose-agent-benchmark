# Copy these protected blocks unchanged into artifacts/solution.i.
[Functions]
  [exact]
    type = ParsedFunction
    expression = '0.5+0.1*exp(-t)*sin(pi*x)*sin(pi*y)'
  []
[]
[Postprocessors]
  [eta_l2]
    type = ElementL2Error
    variable = eta
    function = exact
  []
[]
[Outputs]
  csv = true
  file_base = mms
[]
