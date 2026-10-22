# Copy these protected blocks unchanged into artifacts/solution.i.
[Functions]
  [exact]
    type = ParsedFunction
    expression = '1+sin(pi*x)*sin(pi*y)'
  []
[]
[Postprocessors]
  [p_l2]
    type = ElementL2Error
    variable = p
    function = exact
  []
[]
[Outputs]
  csv = true
  file_base = mms
[]
