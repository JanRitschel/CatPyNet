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
from .DisjunctiveNormalForm import compute
from .MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig
from copy import copy, deepcopy
from ..io.ModelIO import FORMAL_FOOD
# Java modules to find replacements for
'''
import jloda.fx.window.NotificationManager 
import jloda.util.NumberUtils 
import jloda.util.StringUtils 

import java.io.IOException 
import java.util.* 
import java.util.stream.Collectors 

import static catlynet.io.ModelIO.FORMAL_FOOD 
'''

# inintial definition. What is Comparable?
# class Reaction implements Comparable<Reaction>


class Reaction:
    '''*
    * a reaction
    * Daniel Huson, 6.2019
    '''

    def __deepcopy__(self, memo) -> Reaction:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = Reaction(deepcopy(self.name, memo), deepcopy(self.warned_about_suppressing_coefficients, memo),
                             deepcopy(self.reactants, memo), deepcopy(
                                 self.products, memo), deepcopy(self.catalysts, memo),
                             deepcopy(self.inhibitions, memo), deepcopy(
                                 self.reactant_coefficients, memo),
                             deepcopy(self.product_coefficients, memo), deepcopy(self.direction, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, warned_about_suppressing_coefficients: bool = None, 
                 name: str = None, reactants: list = None, 
                 products: list = None, catalysts: list = None, 
                 inhibitions: list = None, reactant_coefficients: dict = None,
                 product_coefficients: dict = None, direction: str = None):
        '''
        Construct a Reaction given all parameters.
        Fills in None for any not given.
        '''
        self.DIRECTION = {"forward": 'forward',
                          "reverse": 'reverse', "both": 'both'}

        self.warned_about_suppressing_coefficients = warned_about_suppressing_coefficients
        self.name = name
        self.reactants = reactants
        self.products = products
        self.catalysts = catalysts
        self.inhibitions = inhibitions
        self.reactant_coefficients = reactant_coefficients
        self.product_coefficients = product_coefficients
        self.direction = direction

    def __init__(self, name: str = None):
        '''
        Construct an empty Reaction with only a name.
        '''
        self.DIRECTION = {"forward": 'forward',
                          "reverse": 'reverse', "both": 'both'}

        self.warned_about_suppressing_coefficients: bool = False
        self.name = name
        self.reactants = []
        self.products = []
        self.catalysts = []
        self.inhibitions = []
        self.reactant_coefficients = {}
        self.product_coefficients = {}
        self.direction = self.DIRECTION["forward"]

    def is_catalyzed_uninhibited_all_reactants(self, food: list[MoleculeType], direction: str) -> bool:
        return False

    def is_catalyzed_uninhibited_all_reactants(self, food_for_reactants: list[MoleculeType], food_for_catalysts: list[MoleculeType],
                                               food_for_inhibitors: list[MoleculeType], direction: str) -> bool:
        return False

    def is_all_reactants(self, food: list[MoleculeType], direction: str) -> bool:
        return False

    def get_direction(self) -> str:
        return self.direction

    def get_name(self) -> str:
        return self.name

    def get_inhibitions(self) -> list:
        return self.inhibitions

    def get_reactants(self) -> list:
        return self.reactants

    def get_products(self) -> list:
        return self.products

    def get_catalysts(self) -> list:
        return self.catalysts

    def set_direction(self, direction: str):
        self.direction = direction

    def set_catalysts(self, catalysts: list = None):
        self.catalysts = catalysts

    def __eq__(self, other: Reaction) -> bool:
        if self == other:
            return True  # FEHLERANFÄLLIG
        if not (isinstance(other, Reaction)):
            return False
        return (self.name == other.name and isinstance(other, Reaction)
                and self.reactants == other.reactants
                and self.products == other.products
                and self.catalysts == other.catalysts
                and self.inhibitions == other.inhibitions
                and self.reactant_coefficients == other.reactant_coefficients
                and self.product_coefficients == other.product_coefficients
                and self.direction == other.direction)

    def __lt__(self, other: Reaction) -> bool:
        return hash(self) < hash(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def parse(self, line: str, aux_reations: list[Reaction], tabbed_format: bool) -> Reaction:
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

        if (colon_pos == -1
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

            print("Can't parse reaction: " + line)
            raise ValueError

        start_arrow: int
        end_arrow: int
        direction: int

        if "<=>" in line:
            self.direction = self.DIRECTION["both"]
            start_arrow = line.find("<=>")
            end_arrow = start_arrow + 2
        elif "=>" in line:
            self.direction = self.DIRECTION["forward"]
            start_arrow = line.find("=>")
            end_arrow = start_arrow + 1
        elif "<=" in line:
            self.direction = self.DIRECTION["reverse"]
            start_arrow = line.find("<=")
            end_arrow = start_arrow + 1
        else:
            print("Can't parse reaction: " + line)
            raise ValueError

        reaction_name = line[0, colon_pos].strip()
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
        reactants = line[colon_pos+1:end_of_reactants].split()
        for r in reactants:
            r = r.strip()

        catalysts: str
        if open_squarebracket == -1:
            catalysts = FORMAL_FOOD.getName()
        else:
            catalysts = line[open_squarebracket+1, close_squarebracket].strip()
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
            inhibitor_string = (line[open_curlybracket+1, close_curlybracket]
                                .strip())
            inhibitor_string = re.sub("\\|", ",", inhibitor_string)
            inhibitor_string = re.sub("\\*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\(\\s*", "(", inhibitor_string)
            inhibitor_string = re.sub("\\s*\\)\\s*", ")", inhibitor_string)
            inhibitor_string = re.sub("\\s*&\\s*", "&", inhibitor_string)
            inhibitor_string = re.sub("\\s*,\\s*", ",", inhibitor_string)
            inhibitor_string = re.sub("\\s+", ",", inhibitor_string)
            inhibitors = inhibitor_string.split(",")
        else:
            inhibitors = [0]

        products = line[end_arrow+1].split("+")  # FEHLERANFÄLLIG/NEU
        reaction = Reaction(reaction_name)
        if all(r.isnumeric() for r in reactants):
            reactant_list = MoleculeType.values_of(names=reactants)
            for r in reactant_list:
                reaction.get_reactants().append(r)
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
                        reaction.get_reactants().append(MoleculeType.value_of(token))
                    if coefficient > 0:
                        reaction.set_reactant_coefficient(
                            MoleculeType.value_of(token), coefficient)
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
            product_list = MoleculeType.values_of(names=products)
            for p in product_list:
                reaction.get_products().append(r)
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
                        reaction.get_products().append(MoleculeType.value_of(token))
                    if coefficient > 0:
                        reaction.set_product_coefficient(
                            MoleculeType.value_of(token), coefficient)
                        if (not (self.warned_about_suppressing_coefficients)):
                            # UNSCHÖN
                            print("Coefficients found in reactions, ignored")
                            self.warned_about_suppressing_coefficients = True
                    coefficient = -1
                if coefficient == -1 and token.isdigit():  # might be problematic, UNSCHÖN
                    coefficient = int(token)
            if coefficient != -1:
                msg = "Can't distinguish between coefficients and product names : "
                for r in products:
                    msg = msg + str(r)
                raise ValueError(msg)

        reaction.set_catalysts(catalysts)
        for inhibitor in inhibitors:  # UNSCHÖN
            reaction.get_inhibitions().append(MoleculeType.value_of(inhibitor))
        reaction.set_direction(direction)

        return reaction

    def get_catalyst_conjunctions(self) -> set[MoleculeType]:  # UNKlAR
        '''
        returns conjunctions of catalysts as a set.
        One element of this set is one permutation of elements that can catalyze the reaction.
        The elements within one element of the set are divided by an "&".
        '''
        conjunctions = []
        dnf = compute(self.get_catalysts())
        for part in dnf.split(","):
            conjunctions.append(MoleculeType.value_of(part))
        return set(conjunctions)

    def get_catalyst_elements(self) -> set[MoleculeType]:  # UNKLAR
        '''
        returns all catalyst elements for this reaction as a set, not considering associations between catalysts.
        '''
        toplevel_conjuncitons = self.get_catalyst_conjunctions()
        all_elements = []
        for conjunction in toplevel_conjuncitons:
            con_elements = conjunction.split("&")
            for element in con_elements:
                all_elements.append(MoleculeType.value_of(element))
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
        match self.get_direction:
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
