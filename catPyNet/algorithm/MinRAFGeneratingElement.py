from __future__ import annotations
from tqdm import tqdm
import random
import copy
from catpynet.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
from catpynet.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from catpynet.algorithm.CoreRAFAlgorithm import CoreRAFAlgorithm
from catpynet.algorithm.AlgorithmBase import AlgorithmBase
from catpynet.model.ReactionSystem import ReactionSystem, MoleculeType
from catpynet.model.Reaction import Reaction, FORMAL_FOOD
from time import time

import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class MinRAFGeneratingElement(AlgorithmBase):

    def __init__(self, targets:list[MoleculeType] = [])-> MinRAFGeneratingElement:
        self.min_i_raf_heuristic = MinIRAFHeuristic()
        self.targets:set[MoleculeType] = targets
    
    NAME: str = "Min RAF Generating Element"
    
    @property
    def number_of_random_insertion_orders(self):
        return self.min_i_raf_heuristic.number_of_random_insertion_orders

    @number_of_random_insertion_orders.setter
    def number_of_random_insertion_orders(self, value: int):
        self.min_i_raf_heuristic.number_of_random_insertion_orders = value
    
    @property
    def name(self):
        return self.NAME

    @name.setter
    def name(self, value: str):
        self.NAME = value

    @property
    def description(self):
        return ("Identifies a subset of the maxRAF that is (i) a RAF and (ii) generates a " + 
                "given element x (not in the food set) and (iii) which is minimal amongst " +
                "all such sets satisfying (i) and (ii)")
        
    def apply(self, input:ReactionSystem) -> ReactionSystem:
        result_sys_name = ""
        if len(self.targets) == 1:
            result_sys_name += self.name + "'" + list(self.targets)[0].name + "'"
        else:
            result_sys_name += self.name + "'" + str(len(self.targets)) + "targets'"
            
        empty_sys = ReactionSystem(result_sys_name)
        
        if not self.targets:
            tqdm.write("No targets selected")
            return empty_sys
        elif input.foods.intersection(self.targets):
            tqdm.write("A target element is contained in the food set.")
            return empty_sys
        
        max_raf = MaxRAFAlgorithm().apply(input)
        if not max_raf.reactions:
            tqdm.write("Max RAF is empty.")
            return empty_sys
        
        augmented_sys = ReactionSystem()
        augmented_sys.foods = max_raf.foods.copy()
        for reaction in tqdm(max_raf.reactions, desc="Augmenting Reactions: "):
            augmented_reaction:Reaction = copy.deepcopy(reaction)
            for target in self.targets:
                augmented_reaction.catalysts = self.add_item_to_all(
                    augmented_reaction.catalyst_conjunctions, target)
            augmented_sys.reactions.append(augmented_reaction)
        
        i_raf = self.min_i_raf_heuristic.apply(augmented_sys)
        i_raf.name = result_sys_name
        if i_raf.size == 0:
            tqdm.write("Irreducible RAF is empty.")
            return empty_sys
        
        core_raf = CoreRAFAlgorithm().apply(augmented_sys)
        if core_raf.size > 0:
            tqdm.write("Irreducible is unique.")
            
        return i_raf
    
    def add_item_to_all(self, conjunctions:set[MoleculeType], item:MoleculeType):
        if not conjunctions or all([conj == FORMAL_FOOD for conj in conjunctions]):
            conjunctions.clear()
            return item.name
        else:
            res = []
            for conj in conjunctions:
                if conj == item: res.append(item)
                else: res.append(MoleculeType().value_of(conj.name + "&" + item.name))
            
            return ",".join(res)