from __future__ import annotations

from ..Utilities import Utilities
from ..model.ReactionSystem import ReactionSystem
from .AlgorithmBase import AlgorithmBase

class MaxRAFAlgorithm (AlgorithmBase):
    
    
    NAME:str = "Max RAF"
    
    def get_name(self) -> str:
        
        return self.NAME
    
    def get_description() -> str:
        
        return "computes the maximal RAF [HMS15] (see also [H23])"
    
    def apply(self, input:ReactionSystem) -> ReactionSystem:
        
        result = ReactionSystem(self.NAME)
        
        input_reactions = set(input.get_reactions)
        input_food = set(input.get_foods)
        
        if len(input_reactions) > 0:
            reactions = []
            molecules = []
            
            reactions.append(input_reactions)
            molecules.append(input_food)
            
            i = 0
            molecules.insert(i+1, Utilities.compute_closure(input_food, reactions[i]))
            reactions.insert(i+1, Utilities.filter_reactions(molecules[i+1], reactions[i]))
            
            while len(reactions[i+1]) < len(reactions[i]):
                molecules.insert(i+1, Utilities.compute_closure(input_food, reactions[i]))
                reactions.insert(i+1, Utilities.filter_reactions(molecules[i+1], reactions[i]))
                i += 1
            
            if len(reactions[i]) > 0:
                result.reactions = reactions[i]
                result.foods = list(result.compute_mentioned_foods(input.foods))
        
        return result