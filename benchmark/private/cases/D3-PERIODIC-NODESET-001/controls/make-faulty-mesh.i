[Mesh]
  [generated]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 4
    ny = 4
    xmax = 1
    ymax = 1
  []
  [left_nodes]
    type = ParsedGenerateNodeset
    input = generated
    expression = 'x < 1e-12'
    new_nodeset_name = left_nodes
  []
  [right_nodes]
    type = ParsedGenerateNodeset
    input = left_nodes
    expression = 'x > 1 - 1e-12'
    new_nodeset_name = right_nodes
  []
  [delete_sides]
    type = BoundaryDeletionGenerator
    input = right_nodes
    boundary_names = 'left right'
  []
[]
