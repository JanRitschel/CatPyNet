from __future__ import annotations

from model.Reaction import Reaction
from model.MoleculeType import MoleculeType
import math
import decimal

    
    
def add_all_mentioned_products(molecules:set[MoleculeType], reactions:list[Reaction]) -> set[MoleculeType]:
    res = molecules
    for reaction in reactions:
        if reaction.direction in {"forward", "both"}:
            res = res.union(reaction.products)
        if reaction.direction in {"reverse", "both"}:
            res = res.union(reaction.reactants)
    return res

def compute_closure(molecules:set[MoleculeType], reactions:list[Reaction]) -> set[MoleculeType]:
    all_molecules = molecules.copy()
    size = -1
    while len(all_molecules) > size:
        size = len(all_molecules)
        for reaction in reactions:
            if reaction.direction in {"forward", "both"}:
                if reaction.reactants.issubset(all_molecules):
                    all_molecules.update(reaction.products)
            if reaction.direction in {"reverse", "both"}:
                if reaction.products.issubset(all_molecules):
                    all_molecules.update(reaction.reactants)
    
    return all_molecules

def filter_reactions(food:set[MoleculeType], reactions:list[Reaction]) -> list[Reaction]:
    res_reactions = []
    for r in reactions:
        if r.is_catalyzed_uninhibited_all_reactants(r.direction, food=food):
            res_reactions.append(r)
    return res_reactions

def compute_food_generated(food:set[MoleculeType], reactions:list[Reaction]) -> list[Reaction]:
    available_food = food
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
                        res = set()
                        if reaction.reactants.issubset(available_food):
                            res.update(reaction.products)
                        if reaction.products.issubset(available_food):
                            res.update(reaction.reactants)
                        available_food.update(res)
            for reaction in to_add: available_reactions.remove(reaction)
        else:
            break
    return closure

def is_float(s:str)-> bool:
    return s.replace(".", "", 1).replace(",", "", 1).isdigit()

def parse_float_input(input: str) -> list | range:

    if "," in input:
        output_ints = input.split(",")
        output_ints = [o.strip() for o in output_ints]
        output = []
        for o in output_ints:
            if is_float(o) and not o.startswith("-", 0, 1):
                output.append(float(o))
    elif "-" in input:
        output = []
        if "/" in input:
            output_ints = [input.split(
                "-")[0]].extend(input.split("-")[1].split("/"))
            while output_ints[0] <= output_ints[1]:
                output.append(output_ints[0])
                output_ints[0] += output_ints[2]
        else:
            output_ints = input.split("-")
            while output_ints[0] <= output_ints[1]:
                output.append(output_ints[0])
                output_ints[0] += 1.0
    else:
        output = [(float(input) if not input.strip().startswith("-", 0, 1)
                and is_float(input.strip()) else None)]

    return output

def parse_integer_input(input: str) -> list | range:

    if "," in input:
        output_ints = input.split(",")
        output = []
        for o in output_ints:
            if o.strip().isdigit():
                output.append(int(o.strip()))
    elif "-" in input:
        if "/" in input:
            output_ints = [input.split("-")[0]]
            output_ints.extend(input.split("-")[1].split("/"))
            output_ints = [int(output_int) for output_int in output_ints]
            output = range(output_ints[0], output_ints[1], output_ints[2])
        else:
            output_ints = input.split("-")
            output_ints = [int(output_int) for output_int in output_ints]
            output = range(output_ints[0], output_ints[1])
    else:
        output = [int(input) if input.strip().isdigit() else None]

    return output

def binom_dist(n: int, p: float) -> list[float]:

    dist = []
    p_of_eq_k = []
    for k in range(n+1):
        p_of_eq_k.append(decimal.Decimal(math.comb(n, k)) *
                         decimal.Decimal(p**k) * decimal.Decimal((1-p)**(n-k)))
        dist.append(sum(p_of_eq_k))
        if sum(p_of_eq_k) == sum(p_of_eq_k[:-1]):
            break 
    return dist

def replace_parameters(input_str: str, 
                       parameters: dict[str:int, str:int, str:int, str:float, str:int]) -> str:
    
    if "." in str(parameters['m']):
        mean_str = str(parameters['m']).replace('.', "-")
    else:
        mean_str = str(parameters['m'])
        
    return (input_str.replace("#a", str(parameters["a"]))
            .replace("#k", str(parameters["k"]))
            .replace("#n", str(parameters["n"]))
            .replace("#m", mean_str)
            .replace("#r", str(parameters["r"])))