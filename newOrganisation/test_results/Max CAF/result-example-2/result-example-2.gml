graph [
  directed 1
  name "Max CAF"
  node [
    id 0
    label "1"
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
    label "11"
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
    label "0"
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
    label "1110"
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
    label "101"
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
    id 5
    label "11100"
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
    id 6
    label "10"
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
    id 7
    label "r4"
    graphics [
      NodeShape "TRIANGLE"
      fill "#FFFFFF"
    ]
    att [
      node_type "reaction"
    ]
  ]
  node [
    id 8
    label "r3"
    graphics [
      NodeShape "TRIANGLE"
      fill "#FFFFFF"
    ]
    att [
      node_type "reaction"
    ]
  ]
  node [
    id 9
    label "r5"
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
    target 8
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 1
    target 7
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 2
    target 8
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
    target 9
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
    target 9
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
    target 7
    graphics [
      fill "#00FF00"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "catalyst"
    ]
  ]
  edge [
    source 4
    target 9
    graphics [
      fill "#00FF00"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "catalyst"
    ]
  ]
  edge [
    source 6
    target 7
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 6
    target 8
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "reactant"
    ]
  ]
  edge [
    source 7
    target 3
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "product"
    ]
  ]
  edge [
    source 8
    target 4
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "product"
    ]
  ]
  edge [
    source 9
    target 5
    graphics [
      fill "#000000"
      ArrowShape "Arrow"
    ]
    att [
      edge_type "product"
    ]
  ]
]
