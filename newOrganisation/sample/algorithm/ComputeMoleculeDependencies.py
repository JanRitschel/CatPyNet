from __future__ import annotations

from .ComputeReactionDependencies import collect_all_ancestors
from .IDescribed import IDescribed
from ..model.ReactionSystem import ReactionSystem

class ComputeMoleculeDependencies(IDescribed):
    
    
    def getDescription():
        return "computes the graph of dependencies between all molecules [HXRS23]"
    
    def apply(input_reaction_system:ReactionSystem, graph_0:Graph) -> Graph:
        pass