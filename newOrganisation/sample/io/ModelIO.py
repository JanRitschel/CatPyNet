from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sample.model.MoleculeType import MoleculeType
from sample.model.Reaction import Reaction
from sample.model.ReactionSystem import ReactionSystem

from sample.settings.ReactionNotation import ReactionNotation
from sample.settings.ArrowNotation import ArrowNotation

import re

FORMAL_FOOD = MoleculeType().value_of(name="$")

class ModelIO:
    

    def parse_food(a_line:str) -> list[MoleculeType]:
        
        a_line = re.sub(" +", " ",a_line.replace(",", " "))
        if a_line.startswith("Food:"):
            if len(a_line) > len("Food:"):
                a_line = a_line.removeprefix("Food:").strip()
            else:
                a_line = ""
        elif a_line.startswith("Food"):
            if len(a_line) > len("Food"):
                a_line = a_line.removeprefix("Food").strip()
            else:
                a_line = ""
        elif a_line.startswith("F:"):
            if len(a_line) > len("F:"):
                a_line = a_line.removeprefix("F:").strip()
            else:
                a_line = ""
        
        result = []
        for name in a_line.split():
            result.append(MoleculeType().value_of(name))
        return result
    
    def read(reaction_system:ReactionSystem, filename:str, reaction_notation: ReactionNotation) -> str:
        """Reads File into a Reactionsystem

        Args:
            reaction_system (ReactionSystem): ReactionSystem to be filled
            filename (str): path to file
            reaction_notation (ReactionNotation): Reaction Format. i.e. TABBED

        Raises:
            IOError: Multiple Reactions with the same name detected

        Returns:
            str: leading comments of the file
        """        
        reaction_names:set[str] = set()
        #aux_reactions:set[Reaction] = set()
        in_leading_comments:bool = True
        leading_comments:list[str] = []
        global FORMAL_FOOD
        
        with open(filename, "r") as f:
            lines = f.readlines()    
            for i, line in enumerate(lines):
                if not line.startswith("#"):
                    in_leading_comments = False
                    line = line.strip()
                    if len(line) > 0:
                        try:
                            arrow_bool = not any([arrow in line for arrow in ["->", "=>", "<-", "<="]])
                            if (line.startswith("Food:") 
                                or (line.startswith("F:") 
                                    and arrow_bool)):
                                reaction_system.foods.extend(ModelIO.parse_food(line))
                            else:
                                print(line)
                                reaction = Reaction().parse(line, reaction_notation)
                                if reaction.name in reaction_names:
                                    raise IOError("Multiple reactions have the same name:\t" + reaction.name)
                                reaction_system.reactions.append(reaction)
                                reaction_names.add(reaction.name)
                                if FORMAL_FOOD.name in reaction.catalysts and not FORMAL_FOOD in reaction_system.foods:
                                    reaction_system.foods.append(FORMAL_FOOD)
                        except IOError as e:
                            msg = e.args[0]
                            raise IOError(msg, i)
                elif in_leading_comments:
                    leading_comments.append(line + "\n")
                    
        return leading_comments
    
    def get_rs_as_str(reaction_system: ReactionSystem, include_food:bool, reaction_notation:ReactionNotation, arrow_notation:ArrowNotation) -> str:
        try:
            return ModelIO.write(reaction_system, include_food, reaction_notation, arrow_notation)
        except IOError as e:
            return ""
        
    def write(self, reaction_system:ReactionSystem, include_food:bool, reaction_notation:ReactionNotation, arrow_notation:ArrowNotation, food_first:bool = True) -> str:
        res = ""
        if food_first and include_food:
                res += "Food: " + ModelIO().get_food_str(reaction_system, reaction_notation) + "\n\n"
            
        for reaction in reaction_system.reactions:
            res += ModelIO().get_reaction_str(reaction, reaction_notation, arrow_notation) + "\n"
        
        if not food_first and include_food:
                res += "Food: " + ModelIO().get_food_str(reaction_system, reaction_notation) + "\n\n"
        return res
            
    def get_food_str(self, reaction_system:ReactionSystem, reaction_notation:ReactionNotation)->str:
        global FORMAL_FOOD
        try:
            foods = reaction_system.foods
            try:foods.remove(FORMAL_FOOD)
            except ValueError: pass
            foods = [food.name for food in reaction_system.foods]
            if reaction_notation == ReactionNotation.FULL: return ", ".join(foods)
            else: return " ".join(foods)
        except IOError:
            return ""
        
    def get_reaction_str(self, reaction:Reaction, reaction_notation:ReactionNotation, arrow_notation:ArrowNotation) -> str:
        res = ""
        sep = " "
        arrow = ""
        match reaction.direction:
            case "forward":
                arrow = " => " if arrow_notation == ArrowNotation.USES_EQUALS else " -> "
            case "reverse":
                arrow = " <= " if arrow_notation == ArrowNotation.USES_EQUALS else " <- "
            case "both":
                arrow = " <=> " if arrow_notation == ArrowNotation.USES_EQUALS else " <-> "
                
        if reaction_notation == ReactionNotation.FULL:
            sep = ","
        if reaction_notation == ReactionNotation.TABBED:
            res = reaction.name + "\t"
            reactants_and_coefficients = []
            for reactant in reaction.reactants:
                try:
                    reactants_and_coefficients.append(str(reaction.reactant_coefficients[reactant.name]) + " " + reactant.name)
                except: reactants_and_coefficients.append(reactant.name)
            res += "+".join(reactants_and_coefficients)
            res += arrow
            products_and_coefficients = []
            for product in reaction.products:
                try:
                    products_and_coefficients.append(str(reaction.product_coefficients[product.name]) + " " + product.name)
                except: products_and_coefficients.append(product.name)
            res += "+".join(products_and_coefficients)    
            res += "\t"
            if reaction.catalysts != "":
                res += "[" + reaction.catalysts + "]"
            if reaction.inhibitions:
                res += "\t{"
                for i, inh in enumerate(reaction.inhibitions):
                    if i == 0:
                        res += inh.name
                    else: res += "," + inh.name
                res += "}"
            return res
        else:
            res = reaction.name + " : "
            reactants_and_coefficients = []
            for reactant in reaction.reactants:
                try:
                    reactants_and_coefficients.append(str(reaction.reactant_coefficients[reactant.name]) + " " + reactant.name)
                except: reactants_and_coefficients.append(reactant.name)
            res += "+".join(reactants_and_coefficients)
            res += " "
            if reaction.catalysts != "":
                cata = reaction.catalysts.replace(",", sep)
                res += "[" + reaction.catalysts + "]"
            if reaction.inhibitions:
                res += " {"
                for i, inh in enumerate(reaction.inhibitions):
                    if i == 0:
                        res += str(inh.name)
                    else: res += sep + inh.name
                res += "}"
            res += arrow
            products_and_coefficients = []
            for product in reaction.products:
                try:
                    products_and_coefficients.append(str(reaction.product_coefficients[product.name]) + " " + product.name)
                except: products_and_coefficients.append(product.name)
            res += "+".join(products_and_coefficients)
            return res