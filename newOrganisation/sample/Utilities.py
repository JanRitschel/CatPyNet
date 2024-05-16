from __future__ import annotations

from .model.Reaction import Reaction #UNSCHÖN, potentiell überflüssig
from .model.MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig

class Utilities:
    
    
    def add_all_mentioned_products(molecules:list[MoleculeType], reactions:list[Reaction]) -> set[MoleculeType]:
        res = set(molecules)
        for reaction in reactions:
            if reaction.direction in {"forward", "both"}:
                res = res.union(reaction.products)
            if reaction.direction in {"reverse", "both"}:
                res = res.union(reaction.reactants)
        return res
    
    def compute_closure(molecules:list[MoleculeType], reactions:list[Reaction]) -> set[MoleculeType]:
        all_molecules = set(molecules)
        size = -1
        while len(all_molecules) > size:
            size = len(all_molecules)
            for reaction in reactions:
                if reaction.direction in {"forward", "both"}:
                    if set(reaction.reactants).issubset(all_molecules):
                        all_molecules = all_molecules.union(reaction.products)
                if reaction.direction in {"reverse", "both"}:
                    if set(reaction.products).issubset(all_molecules):
                        all_molecules = all_molecules.union(reaction.reactants)
        
        return all_molecules
    
    def filter_reactions(food:list[MoleculeType], reactions:list[Reaction]):
        return filter(lambda r: Reaction.is_catalyzed_uninhibited_all_reactants(r, food, direction=r.direction))
        
    
    def contains_all(set:iter, subset:iter) -> bool:
        '''check if iteralble "set" contains all elements of another iterable "subset"'''
        return all(element in set for element in subset)