graph [
  directed 1
  name "Max CAF"
  node [
    id 0
    label "x"
    graphics [
      NodeShape "ELLIPSE"
      fill "#000000"
    ]
    att [
      node_type "molecule"
      Food 1
    ]
  ]
  node [
    id 1
    label "y"
    graphics [
      NodeShape "ELLIPSE"
      fill "#000000"
    ]
    att [
      node_type "molecule"
      Food 1
    ]
  ]
  node [
    id 2
    label "a"
    graphics [
      NodeShape "ELLIPSE"
      fill "#000000"
    ]
    att [
      node_type "molecule"
      Food 1
    ]
  ]
  node [
    id 3
    label "b"
    graphics [
      NodeShape "ELLIPSE"
      fill "#000000"
    ]
    att [
      node_type "molecule"
      Food 1
    ]
  ]
  node [
    id 4
    label "r1"
    graphics [
      NodeShape "TRIANGLE"
      fill "#FFFFFF"
    ]
    att [
      node_type "reaction"
    ]
  ]
  edge [
    source 0
    target 4
    graphics [
      fill "#00FF00"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "catalyst"
    ]
  ]
  edge [
    source 2
    target 4
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 3
    target 4
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 4
    target 1
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "product"
    ]
  ]
]
