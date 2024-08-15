from __future__ import annotations

from ..Utilities import Utilities
from ..model.ReactionSystem import ReactionSystem
from .AlgorithmBase import AlgorithmBase
from .MaxRAFAlgorithm import MaxRAFAlgorithm

import copy
import random

class MinIRAFHeuristic(AlgorithmBase):
    
    
    NAME:str = "iRAF"
    NUMBER_OF_RANDOM_INSERTION_ORDERS:int = 100
    
    @property
    def number_of_random_insertion_orders(self):
        return self.NUMBER_OF_RANDOM_INSERTION_ORDERS
    
    @number_of_random_insertion_orders.setter
    def name(self, value:int):
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
    
    def apply(input: ReactionSystem) -> ReactionSystem|None:
        
        list = MinIRAFHeuristic().apply_all_smallest(input)
        if list != [] and list != None:
            return list[0]
        else: return None

    def apply_all_smallest(self, input:ReactionSystem) -> list[ReactionSystem]:
        
        max_raf = MaxRAFAlgorithm().apply(input)
        reactions = max_raf.reactions
        seeds = [i*123 for i in range(0,self.number_of_random_insertion_orders)]

        best:list[ReactionSystem] = []
        best_size = max_raf.size

        for seed in seeds:
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
        if best==[] or best == None:
            result = copy.copy(max_raf)
            result.name = self.name
            best.append(result)
        
        return best