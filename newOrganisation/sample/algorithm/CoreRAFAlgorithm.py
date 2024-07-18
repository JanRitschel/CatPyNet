from __future__ import annotations

from .Importance import Importance
from ..Utilities import Utilities
from ..model.ReactionSystem import ReactionSystem
from .AlgorithmBase import AlgorithmBase
from .MaxRAFAlgorithm import MaxRAFAlgorithm

class CoreRAFAlgorithm (AlgorithmBase):
    
    
    NAME:str = "Core RAF"
    
    @property
    def name(self) -> str:
        return self.NAME
    
    @property
    def description(self):
        return "computes the unique irreducible RAF, if it exists (Section 4.1 of [SXH20])"
    
    def apply(input:ReactionSystem) -> ReactionSystem:
        max_raf = MaxRAFAlgorithm().apply(input)
        
        important_reactions = ReactionSystem("Important")
        important_reactions.reactions = [p[0].name for p in Importance.compute_reaction_importance(input, max_raf, MaxRAFAlgorithm) if p[1] == 100]
        important_reactions.foods = important_reactions.compute_mentioned_foods(input.foods)
        
        core_raf = MaxRAFAlgorithm().apply(important_reactions)
        core_raf.name = "Core RAF"
        return core_raf