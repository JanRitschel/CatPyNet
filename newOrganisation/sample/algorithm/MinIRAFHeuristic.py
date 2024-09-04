from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from sample.model.ReactionSystem import ReactionSystem
from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm

import copy
import random
from tqdm import tqdm

class MinIRAFHeuristic(AlgorithmBase):
    
    
    NAME:str = "iRAF"
    NUMBER_OF_RANDOM_INSERTION_ORDERS:int = 100
    
    @property
    def number_of_random_insertion_orders(self):
        return self.NUMBER_OF_RANDOM_INSERTION_ORDERS
    
    @number_of_random_insertion_orders.setter
    def number_of_random_insertion_orders(self, value:int):
        self.NUMBER_OF_RANDOM_INSERTION_ORDERS = value

    @property
    def name(self):
        return self.NAME
    
    @name.setter
    def name(self, value:str):
        self.NAME = value
    
    @property
    def description(self):
        return "searches for irreducible RAFs in a heuristic fashion [HS23]"
    
    def apply(self, input: ReactionSystem) -> ReactionSystem|None:
        
        list = MinIRAFHeuristic().apply_all_smallest(input)
        if list:
            return list[0]
        else: return None

    def apply_all_smallest(self, input:ReactionSystem) -> list[ReactionSystem]:
        
        max_raf = MaxRAFAlgorithm().apply(input)
        reactions = max_raf.reactions
        if self.number_of_random_insertion_orders == None: self.number_of_random_insertion_orders = 10
        seeds = [i*123 for i in range(0,self.number_of_random_insertion_orders)]

        best:list[ReactionSystem] = []
        best_size = max_raf.size

        for seed in tqdm(seeds, desc="MinIRafHeuristic: "):
            ordering = reactions
            random.Random(seed).shuffle(ordering)
            work_system = copy.copy(max_raf)
            work_system.name = self.name

            for reaction in ordering:
                work_system.reactions.remove(reaction)
                try:
                    next = MaxRAFAlgorithm().apply(work_system)
                    next.name = self.name
                    if next.size < 0 and next.size <= work_system.size:
                        work_system = next
                        if next.size < best_size:
                            best.clear()
                            best_size = next.size
                        if next.size == best_size and not any([set(next.reactions) == set(a.reactions) for a in best]):
                            best.append(next)
                        if best_size == 1:
                            break
                    else:
                        work_system.reactions.append(reaction)
                except: #UNKLAR, nur wegen Progress?
                    pass
        if best:
            result = copy.copy(max_raf)
            result.name = self.name
            best.append(result)
        
        return best