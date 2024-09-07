from __future__ import annotations

from .model.Reaction import Reaction
from .model.MoleculeType import MoleculeType

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
                        all_molecules.update(reaction.products)
                if reaction.direction in {"reverse", "both"}:
                    if set(reaction.products).issubset(all_molecules):
                        all_molecules.update(reaction.reactants)
        
        return list(all_molecules)
    
    def filter_reactions(food:list[MoleculeType], reactions:list[Reaction]) -> list[Reaction]:
        res_reactions = []
        for r in reactions:
            if r.is_catalyzed_uninhibited_all_reactants(food=food, direction=r.direction):
                res_reactions.append(r)
        return res_reactions
    
    def compute_food_generated(food:list[MoleculeType], reactions:list[Reaction]) -> list[Reaction]:
        available_food = set(food)
        available_reactions = reactions
        closure = []
        while(True):
            to_add = [r for r in available_reactions if r.is_all_reactants(food=available_food, direction=r.direction)]
            if len(to_add) > 0:
                closure.extend(to_add)
                for reaction in to_add:
                    match reaction.direction:
                        case "forward":
                            available_food.update(reaction.products)
                        case "reverse":
                            available_food.update(reaction.reactants)
                        case "both":
                            res = []
                            if set(reaction.reactants).issubset(available_food):
                                res.extend(reaction.products)
                            if set(reaction.products).issubset(available_food):
                                res.extend(reaction.reactants)
                            available_food.update(res)
                for reaction in to_add: available_reactions.remove(reaction)
            else:
                break
        return closure
        
    def contains_all(set:iter, subset:iter) -> bool:
        '''check if iteralble "set" contains all elements of another iterable "subset"'''
        return all(element in set for element in subset)
    
    def is_float(s:str)-> bool:
        return s.replace(".", "", 1).replace(",", "", 1).isdigit()