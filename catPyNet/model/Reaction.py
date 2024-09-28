from __future__ import annotations
from model.MoleculeType import MoleculeType
from copy import copy, deepcopy
from model.DisjunctiveNormalForm import compute
from tqdm import tqdm
import re
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

FORMAL_FOOD = MoleculeType().value_of(name="$")


class Reaction:
    """A reaction.
    """

    """ @property
    def catalysts(self):
        return self._catalysts

    @catalysts.setter
    def catalysts(self, value: str):
        self._catalysts = value
        buffer = self.get_catalyst_conjunctions()
        self._catalyst_conjunctions = buffer """

    def __deepcopy__(self, memo) -> Reaction:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = Reaction(deepcopy(self.name, memo),
                             warned_about_suppressing_coefficients=deepcopy(
                                 self.warned_about_suppressing_coefficients, memo),
                             reactants=deepcopy(self.reactants, memo),
                             products=deepcopy(
                                 self.products, memo),
                             catalysts=deepcopy(self.catalysts, memo),
                             catalyst_conjunctions=deepcopy(
                                 self.catalyst_conjunctions),
                             inhibitions=deepcopy(self.inhibitions, memo),
                             reactant_coefficients=deepcopy(
                                 self.reactant_coefficients, memo),
                             product_coefficients=deepcopy(
                                 self.product_coefficients, memo),
                             direction=deepcopy(self.direction, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, name: str = None, **kwargs) -> Reaction:
        """A Reaction

        Args:
            name (str, optional): name of the reaction. Defaults to None.

        KwArgs:
            reactants (set[MoleculeType]): reactants used in reaction. Defaults to []
            products (list[MoleculeType]): products produced by reaction. Defaults to []
            catalysts (str): catalysts conjunction for reaction. Defaults to ""
            inhibitions (list[MoleculeType]): inhibitions of reaction. Defaults to []
            reactant_coefficients (dict[MoleculeType:float]): reactants mapped to their coefficients. Defaults to {}
            product_coefficients (dict[MoleculeType:float]): products mapped to their coefficients. Defaults to {}
            direction (str): direction the reaction flows in. Defaults to "forward".

        Returns:
            Reaction: the resutling reaction
        """
        self.DIRECTION = {"forward": 'forward',
                          "reverse": 'reverse', "both": 'both'}

        self.warned_about_suppressing_coefficients = False if "warned_about_suppressing_coefficients" not in kwargs else kwargs[
            "warned_about_suppressing_coefficients"]
        self.name = name
        self.reactants: set[MoleculeType] = set(
        ) if "reactants" not in kwargs else kwargs["reactants"]
        self.products: set[MoleculeType] = set(
        ) if "products" not in kwargs else kwargs["products"]
        self.catalysts: str = "" if "catalysts" not in kwargs else kwargs["catalysts"]
        self.catalyst_conjunctions: set[MoleculeType] = set(
        ) if "catalyst_conjunctions" not in kwargs else kwargs["catalyst_conjunctions"]
        self.inhibitions: set[MoleculeType] = set(
        ) if "inhibitions" not in kwargs else kwargs["inhibitions"]
        self.reactant_coefficients = {
        } if "reactant_coefficients" not in kwargs else kwargs["reactant_coefficients"]
        self.product_coefficients = {
        } if "product_coefficients" not in kwargs else kwargs["product_coefficients"]
        self.direction: str = self.DIRECTION["forward"] if "direction" not in kwargs else kwargs["direction"]

    def is_catalyzed_uninhibited_all_reactants(self, direction: str, **kwargs) -> bool:
        """Checks is reaction is uninhibited, catalyzed and has all reactants.

        Args:
            direction (str): direction of the reaction

        KwArgs:\n
        food (set[MoleculeType]): Molecules in food

        food_for_reactants(set[MoleculeType]): Molecules available as reactants
        food_for_catalysts(set[MoleculeType]): Molecules available as catalysts
        food_for_inhibitions(set[MoleculeType]): Molecules available as inhibitions

        Returns:
            bool: True if uninhibited, catalyzed and all reactants present.
                  If any of these are false returns False. 

        Needs either "food"- or all 3 "food_for_..."-kwargs.
        """
        if "food" in kwargs:
            food_set = kwargs["food"]
            return ((direction in {"forward", "both"} and self.reactants.issubset(food_set)
                     or direction in {"reverse", "both"} and self.products.issubset(food_set))
                    and (len(self.catalysts) == 0
                         or any(MoleculeType().values_of(conjunction.name.split("&")).issubset(food_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                         or food_set.isdisjoint(self.inhibitions)))
        else:
            reactant_set = set(
            ) if not "food_for_reactants" in kwargs else kwargs["food_for_reactants"]
            catalyst_set = set(
            ) if not "food_for_catalysts" in kwargs else kwargs["food_for_catalysts"]
            inhibition_set = set(
            ) if not "food_for_inhibitions" in kwargs else kwargs["food_for_inhibitions"]
            return ((direction in {"forward", "both"} and self.reactants.issubset(reactant_set)
                     or direction in {"reverse", "both"} and self.products.issubset(reactant_set))
                    and (len(self.catalysts) == 0
                         or any(MoleculeType().values_of(conjunction.name.split("&")).issubset(catalyst_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                         or not bool(inhibition_set & self.inhibitions)))

    def is_all_reactants(self, food: set[MoleculeType], direction: str) -> bool:
        return (direction in {"forward", "both"}
                and (self.reactants.issubset(food)
                     or direction in {"reverse", "both"})
                and self.products.issubset(food))

    def __eq__(self, other: Reaction | None) -> bool:
        if not (isinstance(other, Reaction)):
            return False
        if self.name != other.name:
            return False
        if self.reactants != other.reactants:
            return False
        if self.products != other.products:
            return False
        if self.catalysts != other.catalysts:
            return False
        if self.inhibitions != other.inhibitions:
            return False
        if self.reactant_coefficients != other.reactant_coefficients:
            return False
        if self.product_coefficients != other.product_coefficients:
            return False
        if self.direction != other.direction:
            return False

        return True

    def __lt__(self, other: Reaction) -> bool:
        return hash(self) < hash(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def parse_new(self, line: str, tabbed_format: bool) -> Reaction:
        """Parses a formatted line to a reaction.

        Args:
            line (str): line describing a reactionin certain formats.
            tabbed_format (bool): true if the format is the tabbed format

        Returns:
            Reaction: reaction represented in line

        Description:
            The accepted formats for the line are a FULL, SPARSE and TABBED format.
            The arrows represent the direction of the reaction with:
                '->' as 'forward'
                '<-' as 'reverse'
                '<->' as 'both'
            They can use '-' or '='.
            The reaction formats can generally be represented by:
            FULL:
            name : [coefficient] reactant ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product ...
            or
            name : [coefficient] reactant +  ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product + ...
            SPARSE:
            name: [coefficient] reactant ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product ...
            or
            name: [coefficient] reactant+ ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product+ ...
            TABBED:
            name \\t [coefficient] reactant ...  -> [coefficient] product ... \\t '[' catalyst ...']' \\t ['{' inhibitor ... '}']
            or
            name \\t [coefficient] reactant+ ... -> [coefficient] product+ ... \\t '[' catalyst ...']' \\t ['{' inhibitor ... '}']
        """
        if line.strip() == "":
            return None

        coefficient_bool = False
        line = line.replace("->", "=>")
        line = line.replace("<-", "<=")
        arrow = "=>"
        direction = self.DIRECTION["forward"]
        if "=>" in line:
            direction = self.DIRECTION["forward"]
            arrow = "=>"
        elif "<=" in line:
            direction = self.DIRECTION["reverse"]
            arrow = "<="
        if "<=>" in line:
            direction = self.DIRECTION["both"]
            arrow = "<=>"

        tabs = line.count("\t")
        tabbed_format = tabs > 1
        if tabbed_format:
            tokens: list[str] = line.split("\t")
            if len(tokens) == 2:
                tokens.append("")
            if len(tokens) == 3:
                tokens.append("")
            re_pro = tokens[1].split(arrow)
            tokens[1] = re_pro[0]
            tokens.append(re_pro[1])
        elif len(line.split("\t")) < 2:
            skipped: list[bool] = []
            for sep in [":", "[", "{", arrow]:
                if sep not in line:
                    skipped.append(True)
                else:
                    skipped.append(False)
                line = line.replace(sep, "\t")
            tokens: list[str] = line.split("\t")
            for i, sep in enumerate(skipped):
                if sep:
                    tokens.insert(i+1, "")
        else:
            tqdm.write("Line " + line + " could not be parsed as the " +
                       "parser was unable to recognize the used format.")
            return Reaction()
        for i, token in enumerate(tokens):
            if tabbed_format:
                token = token.replace("[", "")
                token = token.replace("{", "")
            token = token.replace("]", "")
            token = token.replace("}", "")
            tokens[i] = token.strip()

        token_dict: dict[list | str] = {"r_name": tokens[0],
                                        "reactants": tokens[1],
                                        "reactant_coefficients": {},
                                        "catalysts": tokens[2],
                                        "inhibitions": tokens[3],
                                        "products": tokens[4],
                                        "product_coefficients": {}}
        is_all_numeric = True
        for side in ["reactants", "products"]:
            if "+" in token_dict[side]:
                plus_bool = True
                token_dict[side] = token_dict[side].split("+")
            else:
                plus_bool = False
                token_dict[side] = token_dict[side].split()
            if is_all_numeric:
                is_all_numeric = all([r.replace(".", "").replace(",", "")
                                      .replace(" ", "").isdigit()
                                      for r in token_dict[side]])
        for side in ["reactants", "products"]:
            numeric_buffer = [False, False]
            remove_list = []
            for i, r in enumerate(token_dict[side]):
                r = r.strip()
                if not is_all_numeric:
                    if plus_bool:
                        if " " in r:
                            cache = r.split()
                            if (cache[0].isnumeric() or
                                cache[0].replace(".", "", 1)
                                    .replace(",", "", 1).isdigit()):
                                token_dict[side[:-1] +
                                           "_coefficients"].update({cache[1]: cache[0]})
                                r = cache[1]
                            elif (cache[1].isnumeric() or
                                  cache[1].replace(".", "", 1)
                                  .replace(",", "", 1).isdigit()):
                                token_dict[side[:-1] +
                                           "_coefficients"].append({cache[0]: cache[1]})
                                r = cache[0]
                            else:
                                tqdm.write("There was an unexpected whitespace in reaction: " +
                                           token_dict["r_name"] + " in reactant " +
                                           r)
                    else:
                        numeric_buffer[1] = (r.isnumeric() or r.replace(".", "", 1)
                                             .replace(",", "", 1).isdigit())
                        if numeric_buffer[0] and not numeric_buffer[1]:
                            token_dict[side[:-1] +
                                       "_coefficients"].update({r: token_dict[side][i-1]})
                            remove_list.append(i-1)
                        numeric_buffer[0] = numeric_buffer[1]
                else:
                    if " " in r:
                        if not coefficient_bool:
                            tqdm.write("Coefficients are illegal if all"
                                       + " molecules are numeric. Coeff is "
                                       + "assumed to be first number."
                                       + "\nThe first issue occured at reaction: \n"
                                       + token_dict["r_name"] + " in molecule " + r)
                        r = r.split()[1]

                token_dict[side][i] = r
            for index in reversed(remove_list):
                token_dict[side].pop(index)
        token_dict["inhibitions"] = (token_dict["inhibitions"]
                                     .replace(",", " ").split(" ")
                                     if token_dict["inhibitions"] != "" else [])

        catalysts = token_dict["catalysts"]
        if catalysts == "":
            pass
        else:
            catalysts = self.uniform_logic_notation(catalysts)
        token_dict["catalysts"] = catalysts

        res_reaction = Reaction(token_dict["r_name"],
                                inhibitions=MoleculeType().values_of(
                                    token_dict["inhibitions"]),
                                reactants=MoleculeType().values_of(
                                    token_dict["reactants"]),
                                products=MoleculeType().values_of(
                                    token_dict["products"]),
                                catalysts=token_dict["catalysts"],
                                reactant_coefficients=token_dict["reactant_coefficients"],
                                product_coefficients=token_dict["product_coefficients"],
                                direction=direction)
        return res_reaction

    def get_catalyst_conjunctions(self) -> set[MoleculeType]:
        """
        returns conjunctions of catalysts as a set.
        One element of this set is one permutation of elements that can catalyze the reaction.
        The elements within one element of the set are divided by an "&".

        Returns:
            set[MoleculeType]: separated catalyst conjunctions
        """
        dnf = compute(self.catalysts)
        parts = dnf.split(",")
        return MoleculeType().values_of(parts)

    def get_catalyst_elements(self) -> set[MoleculeType]:
        '''
        returns all catalyst elements for this reaction as a set, not considering associations between catalysts.
        '''
        toplevel_conjuncitons = self.get_catalyst_conjunctions()
        all_elements = set()
        for conjunction in toplevel_conjuncitons:
            all_elements.update(MoleculeType().values_of(
                conjunction.name.split("&")))
        return all_elements

    def any_as_forward(self) -> list[Reaction]:
        """Turns this reaction into a list of equivalent reactions with direction 'forward'

        Returns:
            list[Reaction]: either one or two reactions that, together, are equivalent to self
        """
        match self.direction:
            case "forward":
                return [deepcopy(self)]
            case "reverse":
                reverse = deepcopy(self)
                reverse.swap_reactants_and_products()
                return [reverse]
            case "both":
                forward, reverse = deepcopy(self), deepcopy(self)
                forward.name = forward.name + "[+]"
                reverse.name = reverse.name + "[-]"
                reverse.swap_reactants_and_products()
                return [forward, reverse]

    def swap_reactants_and_products(self):
        self.products, self.reactants = self.reactants, self.products

    def uniform_logic_notation(self, input: str) -> str:
        input = re.sub("\\|", ",", input)
        input = re.sub("\\*", "&", input)
        input = re.sub("\\s*\\(\\s*", "(", input)
        input = re.sub("\\s*\\)\\s*", ")", input)
        input = re.sub("\\s*&\\s*", "&", input)
        input = re.sub("\\s*,\\s*", ",", input)
        input = re.sub("\\s+", ",", input)
        return input
