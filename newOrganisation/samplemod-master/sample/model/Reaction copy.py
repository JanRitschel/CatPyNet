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

from MoleculeType import MoleculeType
from copy import copy, deepcopy
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
class Reaction(type):
    '''*
    * a reaction
    * Daniel Huson, 6.2019
    '''
    
    def __deepcopy__(self, memo) -> Reaction:
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy == None:
            _copy = Reaction(deepcopy(self.name, memo), deepcopy(self.warned_about_suppressing_coefficients, memo), 
                             deepcopy(self.reactants, memo), deepcopy(self.products, memo), deepcopy(self.catalysts, memo), 
                             deepcopy(self.inhibitions, memo), deepcopy(self.reactant_coefficients, memo), 
                             deepcopy(self.product_coefficients, memo), deepcopy(self.direction, memo))
            memo[id_self] = _copy
        return _copy

    def __init__(self, warned_about_suppressing_coefficients: bool = None, name: str = None, reactants: list = None, products: list = None, catalysts: list = None, inhibitions: list = None,
                 reactant_coefficients: dict = None, product_coefficients: dict = None, direction: str = None):
        '''
        Construct a Reaction given all parameters.
        '''
        DIRECTION = {1 : 'forward', 2 : 'reverse', 3 : 'both'}

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
        DIRECTION = {1 : 'forward', 2 : 'reverse', 3 : 'both'}

        self.warned_about_suppressing_coefficients: bool = False
        self.name = name
        self.reactants = []
        self.products = []
        self.catalysts = []
        self.inhibitions = []
        self.reactant_coefficients = {}
        self.product_coefficients = {}
        self.direction = DIRECTION[1]

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
        self.direction = catalysts
    
    def __eq__(self, other: Reaction) -> bool:
        if self == other: return True           #FEHLERANFÄLLIG
        if not(isinstance(other, Reaction)): return False
        return 
        return (self.name == other.name) & isinstance(other, Reaction)
    
    def __lt__(self, other: Reaction) -> bool:
        return hash(self) < hash(other)
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def parse(self, line: str, aux_reations: list[Reaction], tabbed_format: bool)-> Reaction:  #ZU MACHEN
        '''
        parses a reaction
        ReactionNotation:
        name tab: [coefficient] reactant ... '[' catalyst ...']'  ['{' inhibitor ... '}'] -> [coefficient] product ...
        or
        name tab: [coefficient] reactant ... '[' catalyst ... ']'  ['{' inhibitor ... '}'] <- [coefficient] product ...
        or
        name tab: [coefficient] reactant ... '[' catalyst ... ']' ['{' inhibitor ... '}'] <-> [coefficient] product ...
        <p>
        Reactants can be separated by white space or +
        Products can be separated by white space or +
        Catalysts can be separated by white space or , (for or), or all can be separated by & (for 'and')
        '''
        return Reaction('res')
    
    def get_catalyst_conjunctions(self) -> list[MoleculeType]:  #UNKlAR
        '''
        wofür?
        '''
        return []
    
    def get_catalyst_elements(self) -> list[MoleculeType]: #UNKLAR
        '''
        wofür
        '''
        return[]
    
    def get_reactant_coefficient(self, reactant: MoleculeType) -> int:
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.reactant_coefficients[reactant] if self.reactant_coefficients[reactant] else 1
    
    def set_reactant_coefficient(self, reactant: MoleculeType, coefficient: int) -> None:
        if not(reactant in self.reactant_coefficients): self.reactant_coefficients[reactant] = coefficient
        else: print('reactant already in coefficients')
    
    def get_product_coefficient(self, product: MoleculeType):
        '''
        Returns coefficient mapped to reactant in reactand_coefficients.
        If no coefficient is assigned returns 1.
        '''
        return self.product_coefficients[product] if self.product_coefficients[product] else 1
    
    def set_product_coefficient(self, product: MoleculeType, coefficient: int) -> None:
        if not(product in self.product_coefficients): self.product_coefficients[product] = coefficient
        else: print('product already in coefficients')

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
                forward, reverse = deepcopy(self), deepcopy(self) #UNSCHÖN
                forward.name = forward.name + "[+]"
                reverse.name = reverse.name + "[-]"
                reverse.swap_reactants_and_products()
                return [forward, reverse]

    def swap_reactants_and_products(self):
        self.products, self.reactants = self.reactants, self.products

    
        