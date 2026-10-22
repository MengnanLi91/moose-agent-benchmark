# Copy these protected blocks unchanged into artifacts/solution.i.
[Functions]
  [exact]
    type = ParsedFunction
    expression = 'exp(-t)*sin(pi*x)*sin(pi*y)'
  []
[]
[Postprocessors]
  [T_l2]
    type = ElementL2Error
    variable = T
    function = exact
  []
[]
[Outputs]
  csv = true
  file_base = mms
[]
