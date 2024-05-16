from __future__ import annotations
'''
 * ReactionSystem.java Copyright (C) 2022 Daniel H. Huson
 *
 * (Some files contain contributions from other authors, who are then mentioned separately.)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 '''

from .Reaction import Reaction #UNSCHÖN, potentiell überflüssig
from .MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig
from copy import copy

# Java modules to find replacements for
'''
import javafx.beans.binding.Bindings
import javafx.beans.property.*
import javafx.collections.FXCollections
import javafx.collections.ListChangeListener
import javafx.collections.ObservableList
import jloda.util.CollectionUtils

import java.util.*
import java.util.stream.Collectors
'''


class ReactionSystem:
    '''*
    * a catalytic reaction system
    * Daniel Huson, 6.2019
    '''

    def __init__(self, name:str = "Reactions"):
        '''
        construct a reactions system
        '''
        self.name:str = name
        self.reactions:list[Reaction] = []
        self.foods:list[MoleculeType] = []
        self.inhibitors_present:bool = False
        self.size:int
        self.food_size:int
        self.number_of_two_way_reactions:int = 0
        
        self.update_inhibitors_present
        #ENTFERNT, Binds für size und foodsize
        #ENTFERNT, Listener für Reaktionen, der bei hinzufügen/entfernen 
        #von 2-way Reaktionen hoch/runter zählt
    
    @property
    def reactions(self):
        return self._reactions
    @reactions.setter
    def reactions(self, value:list[Reaction]): #FEHLERANFÄLLIG, might cause issues when appending
        self._reactions = value
        buffer = 0
        for reaction in value:
            if reaction.direction == "both":
                buffer += 1
        self._number_of_two_way_reactions = buffer
    
    def __copy__(self) -> ReactionSystem:
        res = ReactionSystem(self.name)
        res.foods = self.foods
        res.reactions = self.reactions
        return res
    
    def make_this_shallow_copy_of(self, other:ReactionSystem) -> None: #UNSCHÖN, wahrscheinlich unnötig
        self.clear
        self.name = other.get_name
        self.foods = other.get_foods
        self.reactions = other.get_reactions
       
    def clear(self) -> None:
        self.reactions.clear
        self.foods.clear
        
    def get_header_line(self) -> str:
        res = [self.name, " has ", str(self.size)]
        if (self.get_number_of_one_way_reactions == 0
            and self.get_number_of_two_way_reactions > 0):
            res.append(" two-way reactions")
        elif (self.get_number_of_one_way_reactions > 0
            and self.get_number_of_two_way_reactions == 0):
            res.append(" one-way reactions")
        elif (self.get_number_of_one_way_reactions > 0
            and self.get_number_of_two_way_reactions > 0):
            res.append(" reactions (")
            res.append(self.get_number_of_two_way_reactions)
            res.append(" two-way and ")
            res.append(self.get_number_of_one_way_reactions)
            res.append(" one-way)")
        else: 
            res.append(" reactions")
        res.append(" on ")
        res.append(len(self.get_foods))
        res.append(" food items")
        return "".join(res)
    
    def update_inhibitors_present(self) -> None:
        """Sets inhibitors_present to True if any inhibitors are present.
        
        Checks all reactions and sets inhibitors_present to true if any
        inhibitor for any reaction is present.
        Otherwise sets inhibitors_present to False
        """        
        for reaction in self.reactions:
            if len(reaction.get_inhibitions) > 0:
                self.inhibitors_present = True
                return
        self.inhibitors_present = False
        
    def get_food_and_reactant_and_product_molecules(self)->list[MoleculeType]: #UNSCHÖN, sollte Set geben
        molecule_types = self.foods
        for reaction in self.get_reactions:
            molecule_types.extend(reaction.get_reactants)
            molecule_types.extend(reaction.get_products)
        return molecule_types
    
    def get_reaction_names(self) -> set[str]: #Unschön, sollte set geben
        names = []
        for reaction in self.get_reactions:
            names.append(reaction.get_name)
        return names
    
    def compute_mentioned_foods(self, foods:list[MoleculeType]) -> set[MoleculeType]:
        """Might need to return a dict?

        Args:
            foods (iter[MoleculeType]): foods to compare reactions against

        Returns:
            set[MoleculeType]: set of all MoleculeTypes mentioned in any reaction and foods
        """
        molecule_types = []
        for reaction in self.get_reactions:
            molecule_types.extend(reaction.get_reactants)
            molecule_types.extend(reaction.get_inhibitions)
            molecule_types.extend(reaction.get_products)
            molecule_types.extend(reaction.get_catalyst_elements) #FEHLERANFÄLLIG, ursprünglich durch get_catalyst_conjunctions
        all_molecules_mentioned = set(molecule_types)
        return all_molecules_mentioned.intersection(foods)
    
    def replace_named_reaction(self, name:str, reaction:Reaction) -> None:
        old_reaction = self.get_reaction(name)
        if old_reaction == None:
            raise TypeError("no such reaction: " + name)
        self.reactions.remove(old_reaction)
        self.reactions.append(reaction)
        
    def sorted_by_hashcode(self) -> ReactionSystem:
        sorted_reaction_system = ReactionSystem(self.get_name)
        sorted_reaction_system.foods = sorted(self.get_foods)
        sorted_reaction_system.reactions = sorted(self.get_reactions)
        return sorted_reaction_system
    
    def get_reaction(self, name:str) -> Reaction:
        for reaction in self.get_reactions: #UNSCHÖN
            if reaction.get_name == name: return reaction
    
    def get_reactions(self) -> list[Reaction]:
        return self.reactions
    
    def get_foods(self) -> list[MoleculeType]:
        return self.foods
    
    def get_size(self) -> int:
        """Returns the number of reactions in the reactions system

        Returns:
            int: size of the reactions system
        """        
        return self.size
    
    #ENTERNT, Properties selbst müssen via self.xx angesteuert werden
    
    def get_food_size(self) -> int:
        return self.food_size
    
    def set_food_size(self, food_size:int):
        self.food_size = food_size
    
    def get_number_of_two_way_reactions(self) -> int:
        return self.number_of_two_way_reactions
    
    def get_number_of_one_way_reactions(self) -> int:
        return self.size - self.number_of_two_way_reactions
    
    def get_name(self) -> str:
        return self.name
    
    def __eq__(self, other:ReactionSystem) -> bool:
        if hash(self) == hash(other): return True #FEHLERANFÄLLIG, temporäre Lösung
        if not (isinstance(other, ReactionSystem)): return False
        return (set(self.foods) == set(other.foods) 
                and set(self.reactions) == set(other.reactions))
        
    def __lt__(self, other:Reaction) -> bool:
        return hash(self) < hash(other)
    
    def __hash__(self) -> int:
        return hash((tuple(self.foods), tuple(self.reactions)))