from __future__ import annotations
import re
from settings.ArrowNotation import ArrowNotation
from settings.ReactionNotation import ReactionNotation
from model.ReactionSystem import ReactionSystem, MoleculeType
from model.Reaction import Reaction, FORMAL_FOOD
from tqdm import tqdm
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

SUPPORTED_OUTPUT_FILE_FORMATS = set([".crs"])

SUPPORTED_INPUT_FILE_FORMATS = set([".crs"])


class ModelIO:

    def parse_food(a_line: str) -> set[MoleculeType]:
        """Determines if a line is a food line and parses to a list of molecules.

        Args:
            a_line (str): line of text

        Returns:
            list[MoleculeType]: list of food molecules or empty list
        """
        a_line = re.sub(" +", " ", a_line.replace(",", " "))
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

        return MoleculeType().values_of(a_line.split())

    def read(reaction_system: ReactionSystem, filename: str, reaction_notation: ReactionNotation) -> str:
        """Prases file into a reaction system

        Args:
            reaction_system (ReactionSystem): ReactionSystem to be filled
            filename (str): path to file
            reaction_notation (ReactionNotation): Reaction Format. i.e. TABBED

        Raises:
            IOError: Multiple Reactions with the same name detected

        Returns:
            str: leading comments of the file
        """
        reaction_names: set[str] = set()
        in_leading_comments: bool = True
        leading_comments: list[str] = []

        with open(filename, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if not line.startswith("#"):
                    in_leading_comments = False
                    line = line.strip()
                    if len(line) > 0:
                        try:
                            arrow_bool = not any(
                                [arrow in line for arrow in ["->", "=>", "<-", "<="]])
                            if (line.startswith("Food:")
                                or (line.startswith("F:")
                                    and arrow_bool)):
                                reaction_system.foods.update(
                                    ModelIO.parse_food(line))
                            else:
                                reaction = Reaction().parse_new(line, reaction_notation)
                                if reaction.name in reaction_names:
                                    raise IOError(
                                        "Multiple reactions have the same name:\t"
                                        + str(reaction.name))
                                reaction_system.reactions.append(reaction)
                                reaction_names.add(reaction.name)
                                if (FORMAL_FOOD.name in reaction.catalysts 
                                    and not FORMAL_FOOD in reaction_system.foods):
                                    reaction_system.foods.add(FORMAL_FOOD)
                        except IOError as e:
                            msg = e.args[0]
                            raise IOError(msg, i)
                elif in_leading_comments:
                    leading_comments.append(line)

        return "\n".join(leading_comments)

    def write(self,
              reaction_system: ReactionSystem,
              include_food: bool,
              reaction_notation: ReactionNotation,
              arrow_notation: ArrowNotation,
              food_first: bool = True) -> str:
        """Parses a reaction system to a str in the format of a '.crs' file.

        Args:
            reaction_system (ReactionSystem): reaction system to be parsed
            include_food (bool): should food be icluded in the file
            reaction_notation (ReactionNotation): Determines reaction notation format i.e. TABBED
            arrow_notation (ArrowNotation): Determines arrow format i.e. USES_EQUALS
            food_first (bool, optional): Should the food be at the beginning or end of the file. Defaults to True.

        Returns:
            str: str format of reaction system
        """        
        if not reaction_system.reactions:
            tqdm.write("The resulting reaction system has no reactions")
            return "The resulting reaction system has no reactions"
        res = ""
        if food_first and include_food:
            res += "Food: " + ModelIO().get_food_str(reaction_system, reaction_notation) + "\n\n"

        for reaction in reaction_system.reactions:
            res += ModelIO().get_reaction_str(reaction, reaction_notation, arrow_notation) + "\n"

        if not food_first and include_food:
            res += "Food: " + ModelIO().get_food_str(reaction_system, reaction_notation) + "\n\n"
        return res

    def get_food_str(self,
                     reaction_system: ReactionSystem,
                     reaction_notation: ReactionNotation) -> str:
        try:
            foods = reaction_system.foods
            foods = [food.name for food in reaction_system.foods]
            foods.sort()
            if reaction_notation == ReactionNotation.FULL:
                return ", ".join(foods)
            else:
                return " ".join(foods)
        except IOError:
            return ""

    def get_reaction_str(self,
                         reaction: Reaction,
                         reaction_notation: ReactionNotation,
                         arrow_notation: ArrowNotation) -> str:
        """str representation of a reaction for a '.crs' file

        Args:
            reaction (Reaction): reacton to be parsed to str
            reaction_notation (ReactionNotation): Determines reaction notation format i.e. TABBED
            arrow_notation (ArrowNotation): Determines arrow format i.e. USES_EQUALS

        Returns:
            str: str representation of a reaction
        """        
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
                    reactants_and_coefficients.append(
                        str(reaction.reactant_coefficients[reactant.name])
                        + " " +
                        reactant.name)
                except:
                    reactants_and_coefficients.append(reactant.name)
            reactants_and_coefficients.sort()
            res += " + ".join(reactants_and_coefficients)
            res += arrow
            products_and_coefficients = []
            for product in reaction.products:
                try:
                    products_and_coefficients.append(
                        str(reaction.product_coefficients[product.name])
                        + " " +
                        product.name)
                except:
                    products_and_coefficients.append(product.name)
            products_and_coefficients.sort()
            res += " + ".join(products_and_coefficients)
            res += "\t"
            if reaction.catalysts != "":
                res += "[" + reaction.catalysts + "]"
            if reaction.inhibitions:
                res += "\t{"
                inh_list = list(reaction.inhibitions)
                inh_list.sort()
                for i, inh in enumerate(inh_list):
                    if i == 0:
                        res += inh.name
                    else:
                        res += "," + inh.name
                res += "}"
            return res
        else:
            res = reaction.name + " : "
            reactants_and_coefficients = []
            for reactant in reaction.reactants:
                try:
                    reactants_and_coefficients.append(
                        str(reaction.reactant_coefficients[reactant.name])
                        + " "
                        + reactant.name)
                except:
                    reactants_and_coefficients.append(reactant.name)
            reactants_and_coefficients.sort()
            res += " + ".join(reactants_and_coefficients)
            res += " "
            if reaction.catalysts != "":
                res += "[" + reaction.catalysts + "]"
            if reaction.inhibitions:
                res += " {"
                inh_list = list(reaction.inhibitions)
                inh_list.sort()
                for i, inh in enumerate(inh_list):
                    if i == 0:
                        res += str(inh.name)
                    else:
                        res += sep + inh.name
                res += "}"
            res += arrow
            products_and_coefficients = []
            for product in reaction.products:
                try:
                    products_and_coefficients.append(
                        str(reaction.product_coefficients[product.name])
                        + " "
                        + product.name)
                except:
                    products_and_coefficients.append(product.name)
            products_and_coefficients.sort()
            res += " + ".join(products_and_coefficients)
            return res
