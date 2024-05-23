from __future__ import annotations

from ..Utilities import Utilities
from ..model.ReactionSystem import ReactionSystem
from .AlgorithmBase import AlgorithmBase

class MaxCAFAlgorithm(AlgorithmBase):
    
    
    NAME:str = "Max CAF"
    
    @property
    def name(self):
        return self.NAME
    
    @name.setter
    def name(self, value:str):
        self.NAME = value
    
    @property
    def description(self):
        return "computes the maximal CAF [HMS15]"
    
    def apply(self, input:ReactionSystem) -> ReactionSystem:
        result = ReactionSystem(self.NAME)
        
        input_reactions = set(input.get_reactions)
        input_food = set(input.get_foods)

        reactions = []
        molecules = []
        
        reactions.append(input_reactions)
        molecules.append(input_food)
        
        i = 1
        molecules.insert(i, Utilities.add_all_mentioned_products(molecules[i-1], reactions[i-1]))
        reactions.insert(i, Utilities.filter_reactions(molecules[i], input_reactions))
        
        while len(reactions[i]) > len(reactions[i-1]):
            molecules.insert(i+1, Utilities.compute_closure(input_food, reactions[i]))
            reactions.insert(i+1, Utilities.filter_reactions(molecules[i+1], reactions[i]))
            i += 1
        
        if len(reactions[i]) > 0:
            result.reactions = reactions[i]
            result.foods = list(result.compute_mentioned_foods(input.foods))
        return result