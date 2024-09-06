from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from tqdm import tqdm

from sample.Utilities import Utilities
from sample.model.ReactionSystem import ReactionSystem
from sample.algorithm.AlgorithmBase import AlgorithmBase

class MaxPseudoRAFAlgorithm (AlgorithmBase):
    
    
    NAME:str = "Max Pseudo RAF"
    
    @property
    def name(self):
        return self.NAME
    
    @name.setter
    def name(self, value:str):
        self.NAME = value
    
    @property
    def description(self):
        return "computes the maximal Pseudo RAF [HMS15]"
    
    def apply(self, input:ReactionSystem) -> ReactionSystem:
        
        result = ReactionSystem(self.NAME)
        
        input_reactions = input.reactions
        input_food = input.foods
        
        if len(input_reactions) > 0:
            reactions = []
            molecules = []
            
            reactions.append(input_reactions)
            molecules.append(input_food)
            
            i = 0
            molecules.insert(i+1, Utilities.add_all_mentioned_products(input_food, reactions[i]))
            reactions.insert(i+1, Utilities.filter_reactions(molecules[i+1], reactions[i]))
            
            while len(reactions[i+1]) < len(reactions[i]):
                i += 1
                molecules.insert(i+1, Utilities.add_all_mentioned_products(input_food, reactions[i]))
                reactions.insert(i+1, Utilities.filter_reactions(molecules[i+1], reactions[i]))
            
            if len(reactions[i]) > 0:
                result.reactions = reactions[i]
                result.foods = list(result.compute_mentioned_foods(input.foods))
        
        return result