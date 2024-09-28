from __future__ import annotations
from algorithm.AlgorithmBase import AlgorithmBase
from model.ReactionSystem import ReactionSystem
import Utilities as Utilities

import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class MaxCAFAlgorithm(AlgorithmBase):

    NAME: str = "Max CAF"

    @property
    def name(self):
        return self.NAME

    @name.setter
    def name(self, value: str):
        self.NAME = value

    @property
    def description(self):
        return "computes the maximal CAF [HMS15]"

    def apply(self, input: ReactionSystem) -> ReactionSystem:
        """Computes the maximal CAF

        Args:
            input (ReactionSystem): system to be computed

        Returns:
            ReactionSystem: maximal CAF
        """        
        result = ReactionSystem(self.NAME)

        input_reactions = set(input.reactions)
        input_food = input.foods

        molecules = [input_food]
        reactions = [Utilities.filter_reactions(input_food, input_reactions)]

        i = 0
        molecules.insert(
            i+1, Utilities.add_all_mentioned_products(molecules[i], 
                                                      reactions[i]))
        reactions.insert(
            i+1, Utilities.filter_reactions(molecules[i+1], input_reactions))

        while len(reactions[i+1]) > len(reactions[i]):
            i += 1
            molecules.insert(
                i+1, Utilities.add_all_mentioned_products(molecules[i], 
                                                          reactions[i]))
            reactions.insert(
                i+1, Utilities.filter_reactions(molecules[i+1], 
                                                input_reactions))

        if len(reactions[i+1]) > 0:
            result.reactions = reactions[i+1]
            result.foods = result.compute_mentioned_foods(input.foods)
        return result
