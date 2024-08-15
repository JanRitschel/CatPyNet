from __future__ import annotations
'''
 * Reaction.java Copyright (C) 2022 Daniel H. Huson
 *
 * (Some files contain contributions from other authors, who are then mentioned separately.)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY  without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 '''

import re
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from sample.model.DisjunctiveNormalForm import compute
from sample.model.MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig
from copy import copy, deepcopy


FORMAL_FOOD = MoleculeType().value_of(name="$")

class Reaction:
    '''*
    * a reaction
    * Daniel Huson, 6.2019
    '''

    def __deepcopy__(self, memo) -> Reaction:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = Reaction(deepcopy(self.name, memo), warned_about_suppressing_coefficients = deepcopy(self.warned_about_suppressing_coefficients, memo),
                             reactants = deepcopy(self.reactants, memo), products = deepcopy(
                                 self.products, memo), catalysts = deepcopy(self.catalysts, memo),
                             inhibitions = deepcopy(self.inhibitions, memo), reactant_coefficients = deepcopy(
                                 self.reactant_coefficients, memo),
                             product_coefficients = deepcopy(self.product_coefficients, memo), direction = deepcopy(self.direction, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, name: str = None, **kwargs) -> Reaction:        
        
        self.DIRECTION = {"forward": 'forward',
                          "reverse": 'reverse', "both": 'both'}

        self.warned_about_suppressing_coefficients = False if "warned_about_suppressing_coefficients" not in kwargs else kwargs["warned_about_suppressing_coefficients"]
        self.name = name
        self.reactants:list[MoleculeType] = [] if "reactants" not in kwargs else kwargs["reactants"]
        self.products:list[MoleculeType] = [] if "products" not in kwargs else kwargs["products"]
        self.catalysts:str = "" if "catalysts" not in kwargs else kwargs["catalysts"]
        self.inhibitions:list[MoleculeType] = [] if "inhibitions" not in kwargs else kwargs["inhibitions"]
        self.reactant_coefficients = {} if "reactant_coefficients" not in kwargs else kwargs["reactant_coefficients"]
        self.product_coefficients = {} if "product_coefficients" not in kwargs else kwargs["product_coefficients"]
        self.direction:str = self.DIRECTION["forward"] if "direction" not in kwargs else kwargs["direction"]

    def is_catalyzed_uninhibited_all_reactants(self, direction: str, **kwargs) -> bool:
        """Checks is reaction is uninhibited, catalyzed and has all reactants.

        Args:
            direction (str): direction of the reaction
            food (list[MoleculeType]): Molecules in food
            
            food_for_reactants(list[MoleculeType]): Molecules available as reactants
            food_for_catalysts(list[MoleculeType]): Molecules available as catalysts
            food_for_inhibitions(list[MoleculeType]): Molecules available as inhibitions
            
        Returns:
            bool: True if uninhibited, catalyzed and all reactants present.
                  If any of these are false returns false. 
        """        
        if "food" in kwargs:
            food_set = set(kwargs["food"])
            return ((direction in {"forward", "both"} and set(self.reactants).issubset(food_set)
                        or direction in {"reverse", "both"} and set(self.products).issubset(food_set))
                    and (len(self.catalysts) == 0 
                        or any(set(MoleculeType().values_of(conjunction.name.split("&"))).issubset(food_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                        or food_set.isdisjoint(self.inhibitions)))
        else:
            reactant_set = set() if not "food_for_reactants" in kwargs else set(kwargs["food_for_reactants"])
            catalyst_set = set() if not "food_for_catalysts" in kwargs else set(kwargs["food_for_catalysts"])
            inhibition_set = set() if not "food_for_inhibitions" in kwargs else set(kwargs["food_for_inhibitions"])
            return ((direction in {"forward", "both"} and set(self.reactants).issubset(reactant_set)
                        or direction in {"reverse", "both"} and set(self.products).issubset(reactant_set))
                    and (len(self.catalysts) == 0 
                        or any(set(MoleculeType().values_of(conjunction.name.split("&"))).issubset(catalyst_set) for conjunction in self.get_catalyst_conjunctions()))
                    and (len(self.inhibitions) == 0
                        or not bool(inhibition_set & set(self.inhibitions))))

    """ def is_catalyzed_uninhibited_all_reactants(self, food_for_reactants: list[MoleculeType], food_for_catalysts: list[MoleculeType],
                                               food_for_inhibitors: list[MoleculeType], direction: str) -> bool:
        return False
 """
    def is_all_reactants(self, food: set[MoleculeType], direction: str) -> bool:
        return (direction in {"forward", "both"} and set(self.reactants).issubset(food)
                    or direction in {"reverse", "both"} and set(self.products).issubset(food))

    def __eq__(self, other: Reaction) -> bool:
        if not (isinstance(other, Reaction)):
            return False
        res = True
        #print("self: " + self.name + "; other: " + other.name)
        if not self.name == other.name and isinstance(other, Reaction): res = False; #print("failed at name")
        if not self.reactants == other.reactants: res = False; #print("failed at reactants")
        if not self.products == other.products: res = False; #print("failed at products")
        if not self.catalysts == other.catalysts: res = False; #print("failed at catalysts")
        if not self.inhibitions == other.inhibitions: res = False; #print("failed at inhibitions")
        if not self.reactant_coefficients == other.reactant_coefficients: res = False; #print("failed at reactant_coefficients")
        if not self.product_coefficients == other.product_coefficients: res = False; #print("failed at product_coefficients")
        if not self.direction == other.direction: res = False; #print("failed at product_coefficients")

        return res
        """ return (self.name == other.name and isinstance(other, Reaction)
                and self.reactants == other.reactants
                and self.products == other.products
                and self.catalysts == other.catalysts
                and self.inhibitions == other.inhibitions
                and self.reactant_coefficients == other.reactant_coefficients
                and self.product_coefficients == other.product_coefficients
                and self.direction == other.direction) """

    def __lt__(self, other: Reaction) -> bool:
        return hash(self) < hash(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def parse(self, line: str, tabbed_format: bool) -> Reaction: #aux_reations: list[Reaction],
        '''
        parses a reaction
        ReactionNotation:
        name <tab>: [coefficient] reactant ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product ...
        or
        name <tab>: [coefficient] reactant ... '[' catalyst ... ']'  ['{' inhibitor ... '}'] <- [coefficient] product ...
        or
        name <tab>: [coefficient] reactant ... '[' catalyst ... ']' ['{' inhibitor ... '}'] <-> [coefficient] product ...
        <p>
        Reactants can be separated by white space or +
        Products can be separated by white space or +
        Catalysts can be separated by white space or , (for or), or all can be separated by & (for 'and')

        The tabbed format is:
        name <tab> [coefficient] reactant ... -> [coefficient] product ... <tab> '[' catalyst ...']'  <tab> ['{' inhibitor ... '}']
        '''
        line = line.replace("->", "=>")
        line = line.replace("<-", "<=")

        if tabbed_format:
            tokens = line.split('\t')
            for t in tokens:
                t = t.strip()
            if len(tokens) == 3 or len(tokens) == 4:
                if tokens[1].find("<=") == -1:
                    arrow_start = tokens[1].find("=>")
                else:
                    arrow_start = tokens[1].index("<=")

                if arrow_start != -1:
                    if len(tokens) == 3:
                        line = (tokens[0] + ": " + tokens[1][0:arrow_start]
                                + " [" + tokens[2] + "] "
                                + tokens[1][arrow_start:len(tokens[1])-1])
                    else:
                        line = (tokens[0] + ": " + tokens[1][0:arrow_start] + " [" + tokens[2] +
                                "] " + " {" + tokens[3] + "} " +
                                tokens[1][arrow_start:len(tokens[1])-1])

        colon_pos = line.find(':')
        open_squarebracket = line.find('[')
        close_squarebracket = line.find(']')
        open_curlybracket = line.find('{')
        close_curlybracket = line.find('}')

        if ((colon_pos == -1 and not tabbed_format)
            or (open_squarebracket != -1
                and (open_squarebracket < colon_pos
                     or close_squarebracket < open_squarebracket))
            or (open_squarebracket == -1
                and close_squarebracket != -1)
            or (open_curlybracket != -1
                and (open_curlybracket < colon_pos
                     or close_curlybracket < open_curlybracket))
            or (open_curlybracket == -1
                and close_curlybracket != -1)):

            print("colon deosn't exist" + str(colon_pos == -1 and not tabbed_format))
            print("opensquare exist" + str((open_squarebracket != -1
                and (open_squarebracket < colon_pos
                     or close_squarebracket < open_squarebracket))))
            print("opensquare deosn't exist" + str((open_squarebracket == -1
                and close_squarebracket != -1)))
            print("opencurly exist" + str((open_curlybracket != -1
                and (open_curlybracket < colon_pos
                     or close_curlybracket < open_curlybracket))))
            print("opencurly doesn't exist" + str(open_curlybracket == -1
                and close_curlybracket != -1))
            print("Can't parse reaction due to missing/misplaced bracket/colon: " + line)
            raise ValueError

        start_arrow: int
        end_arrow: int
        direction: int

        if "<=>" in line:
            direction = self.DIRECTION["both"]
            start_arrow = line.find("<=>")
            end_arrow = start_arrow + 2
        elif "=>" in line:
            direction = self.DIRECTION["forward"]
            start_arrow = line.find("=>")
            end_arrow = start_arrow + 1
        elif "<=" in line:
            direction = self.DIRECTION["reverse"]
            start_arrow = line.find("<=")
            end_arrow = start_arrow + 1
        else:
            print("Can't parse reaction due to missing arrow: " + line)
            raise ValueError

        reaction_name = line[0:colon_pos].strip()
        end_of_reactants: int

        if open_squarebracket != -1:
            end_of_reactants = open_squarebracket
        elif open_squarebracket == -1:
            if open_curlybracket != -1:
                end_of_reactants = open_curlybracket
            elif open_curlybracket == -1:
                end_of_reactants = start_arrow
            else:
                print('''open_curlybracket has no int value.
                      Can't parse reaction: ''' + line)
                raise ValueError
        else:
            print('''open_squarebracket has no int value.
                      Can't parse reaction: ''' + line)
            raise ValueError
        if "+" in line[colon_pos+1:end_of_reactants]:
            reactants = line[colon_pos+1:end_of_reactants].strip().split("+")
        else: reactants = line[colon_pos+1:end_of_reactants].strip().split()
        """ for r in reactants:
            r = r.strip() """

        catalysts: str
        if open_squarebracket == -1:
            global FORMAL_FOOD
            catalysts = FORMAL_FOOD.name
        else:
            catalysts = line[open_squarebracket+1:close_squarebracket].strip().strip("[").strip("]")
            catalysts = re.sub("\\|", ",", catalysts)
            catalysts = re.sub("\\*", "&", catalysts)
            catalysts = re.sub("\\s*\\(\\s*", "(", catalysts)
            catalysts = re.sub("\\s*\\)\\s*", ")", catalysts)
            catalysts = re.sub("\\s*&\\s*", "&", catalysts)
            catalysts = re.sub("\\s*,\\s*", ",", catalysts)
            catalysts = re.sub("\\s+", ",", catalysts)

        inhibitors: list
        # UNSCHÖN
        if open_curlybracket != -1 and close_curlybracket != -1:
            inhibitor_string = (line[open_curlybracket+1:close_curlybracket]
                                .strip().strip("{").strip("}"))
            inhibitor_string = re.sub("\\|", ",", inhibitor_string)
            inhibitor_string = re.sub("\\*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\(\\s*", "(", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\)\\s*", ")", inhibitor_string)
            inhibitor_string = re.sub("\\s*&\\s*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*,\\s*", ",", inhibitor_string)
            inhibitor_string = re.sub("\\s+", ",", inhibitor_string)
            inhibitors = inhibitor_string.split(",")
        else:
            inhibitors = []

        if "+" in line[end_arrow+1:]:
            products = line[end_arrow+1:].strip().split("+")  # FEHLERANFÄLLIG/NEU
        else: products = line[end_arrow+1:].strip().split()
        """ cache = []
        for p in products:
            cache.extend(p.split(" "))
        products = cache """
        reaction = Reaction(reaction_name)
        if all(r.isnumeric() for r in reactants):
            reactant_list = MoleculeType().values_of(names=reactants)
            for r in reactant_list:
                reaction.reactants.append(r)
        else:
            coefficient = -1
            for token in reactants:
                if token.isdigit():  # might be problematic, UNSCHÖN
                    if coefficient == -1:
                        coefficient = int(token)
                    else:
                        print(
                            "Can't distinguish between coefficients and reactant names : ")
                        print(reactants)
                        raise ValueError
                else:
                    if coefficient == -1 or coefficient > 0:
                        reaction.reactants.append(MoleculeType().value_of(token))
                    if coefficient > 0:
                        reaction.set_reactant_coefficient(
                            MoleculeType().value_of(token), coefficient)
                        if (not (self.warned_about_suppressing_coefficients)):
                            print("Coefficients found in reactions, ignored")
                            self.warned_about_suppressing_coefficients = True
                    coefficient = -1
                if coefficient == -1 and token.isdigit():  # might be problematic, UNSCHÖN
                    coefficient = int(token)
            if coefficient != -1:
                msg = "Can't distinguish between coefficients and reactant names : "
                for r in reactants:
                    msg = msg + str(r)
                raise ValueError(msg)

        if all(p.isnumeric() for p in products):
            product_list = MoleculeType().values_of(names=products)
            for p in product_list:
                reaction.products.append(p)
        else:
            coefficient = -1
            for token in products:
                if token.isdigit():  # might be problematic, UNSCHÖN
                    if coefficient == -1:
                        coefficient = int(token)
                    else:
                        msg = "Can't distinguish between coefficients and product names : "
                        for r in products:
                            msg = msg + str(r)
                        raise ValueError(msg)
                else:
                    if coefficient == -1 or coefficient > 0:
                        reaction.products.append(MoleculeType().value_of(token))
                    if coefficient > 0:
                        reaction.set_product_coefficient(
                            MoleculeType().value_of(token), coefficient)
                        if (not (self.warned_about_suppressing_coefficients)):
                            # UNSCHÖN
                            print("Coefficients found in reactions, ignored")
                            self.warned_about_suppressing_coefficients = True
                    coefficient = -1
                """ if coefficient == -1 and token.isdigit():  # might be problematic, UNSCHÖN
                    coefficient = int(token) """
            if coefficient != -1:
                msg = "Can't distinguish between coefficients and product names : "
                for r in products:
                    msg = msg + str(r)
                raise ValueError(msg)

        reaction.catalysts = catalysts
        for inhibitor in inhibitors:  # UNSCHÖN
            reaction.inhibitions.append(MoleculeType().value_of(inhibitor))
        reaction.direction = direction

        return reaction

    def get_catalyst_conjunctions(self) -> set[MoleculeType]:
        '''
        returns conjunctions of catalysts as a set.
        One element of this set is one permutation of elements that can catalyze the reaction.
        The elements within one element of the set are divided by an "&".
        '''
        conjunctions = []
        dnf = compute(self.catalysts)
        parts = dnf.split(",")
        return set(MoleculeType().values_of(parts))
        """ for part in dnf.split(","):
            conjunctions.append(MoleculeType().value_of(part))
        return set(conjunctions) """

    def get_catalyst_elements(self) -> set[MoleculeType]:
        '''
        returns all catalyst elements for this reaction as a set, not considering associations between catalysts.
        '''
        toplevel_conjuncitons = self.get_catalyst_conjunctions()
        all_elements = []
        for conjunction in toplevel_conjuncitons:
            con_elements = conjunction.name.split("&")
            for element in con_elements:
                all_elements.append(MoleculeType().value_of(element))
        return set(all_elements)

    def get_reactant_coefficient(self, reactant: MoleculeType) -> int:
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.reactant_coefficients[reactant] if self.reactant_coefficients[reactant] else 1

    def set_reactant_coefficient(self, reactant: MoleculeType, coefficient: int) -> None:
        if not (reactant in self.reactant_coefficients):
            self.reactant_coefficients[reactant] = coefficient
        else:
            print('reactant already in coefficients')

    def get_product_coefficient(self, product: MoleculeType):
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.product_coefficients[product] if self.product_coefficients[product] else 1

    def set_product_coefficient(self, product: MoleculeType, coefficient: int) -> None:
        if not (product in self.product_coefficients):
            self.product_coefficients[product] = coefficient
        else:
            print('product already in coefficients')

    def any_as_forward(self) -> list[Reaction]:
        '''
        turns this reaction into a list of reactions with the direction forward
        '''
        match self.direction:
            case "forward":
                return [deepcopy(self)]
            case "reverse":
                reverse = deepcopy(self)
                reverse.swap_reactants_and_products()
                return [reverse]
            case "both":
                forward, reverse = deepcopy(self), deepcopy(self)  # UNSCHÖN
                forward.name = forward.name + "[+]"
                reverse.name = reverse.name + "[-]"
                reverse.swap_reactants_and_products()
                return [forward, reverse]

    def swap_reactants_and_products(self):
        self.products, self.reactants = self.reactants, self.products
