from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
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

from sample.model.Reaction import Reaction #UNSCHÖN, potentiell überflüssig
from sample.model.MoleculeType import MoleculeType #UNSCHÖN, potentiell überflüssig


class ReactionSystem:
    '''*
    * a catalytic reaction system
    * Daniel Huson, 6.2019
    '''

    def __init__(self, name:str = "Reactions", **kwargs):
        '''
        construct a reaction system
        '''
        self.name:str = name        
        self.reactions:list[Reaction] = [] if "reactions" not in kwargs else kwargs["reactions"]
        self.foods:list[MoleculeType] = [] if "foods" not in kwargs else kwargs["foods"]
        self.inhibitors_present:bool = False
        self.size:int
        self.food_size:int
        buffer = 0
        for reaction in self.reactions:
            if reaction.direction == "both":
                buffer += 1
        self.number_of_two_way_reactions:int = buffer
        
        self.update_inhibitors_present()
        #ENTFERNT, Binds für size und foodsize
    
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

    @property
    def size(self):
        return len(self.reactions)
    
    @property
    def food_size(self):
        return len(self.foods)
    
    def __copy__(self) -> ReactionSystem:
        res = ReactionSystem(self.name)
        res.foods = self.foods
        res.reactions = self.reactions
        return res
    
    def make_this_shallow_copy_of(self, other:ReactionSystem) -> None: #UNSCHÖN, wahrscheinlich unnötig
        self.clear
        self.name = other.name
        self.foods = other.foods
        self.reactions = other.reactions
       
    def clear(self) -> None:
        self.reactions.clear
        self.foods.clear
        
    def get_header_line(self) -> str:
        res = [self.name, " has ", str(self.size)]
        if (self.get_number_of_one_way_reactions() == 0
            and self.number_of_two_way_reactions > 0):
            res.append(" two-way reactions")
        elif (self.get_number_of_one_way_reactions() > 0
            and self.number_of_two_way_reactions == 0):
            res.append(" one-way reactions")
        elif (self.get_number_of_one_way_reactions() > 0
            and self.number_of_two_way_reactions > 0):
            res.append(" reactions (")
            res.append(self.number_of_two_way_reactions)
            res.append(" two-way and ")
            res.append(self.get_number_of_one_way_reactions())
            res.append(" one-way)")
        else: 
            res.append(" reactions")
        res.append(" on ")
        res.append(len(self.foods))
        res.append(" food items")
        return "".join(res)
    
    def update_inhibitors_present(self) -> None:
        """Sets inhibitors_present to True if any inhibitors are present.
        
        Checks all reactions and sets inhibitors_present to true if any
        inhibitor for any reaction is present.
        Otherwise sets inhibitors_present to False
        """        
        for reaction in self.reactions:
            if len(reaction.inhibitions) > 0:
                self.inhibitors_present = True
                return
        self.inhibitors_present = False
        
    def get_mentioned_molecules(self)->set[MoleculeType]:
        molecule_types = self.foods
        for reaction in self.reactions:
            molecule_types.extend(reaction.reactants)
            molecule_types.extend(reaction.products)
            molecule_types.extend(reaction.inhibitions)
            catalysts = MoleculeType().values_of(reaction.catalysts.replace(",","\t")
                                                 .replace("|","\t").replace("*", "\t")
                                                 .replace("&", "\t").split("\t"))
            molecule_types.extend(catalysts)
        return set(molecule_types)
    
    def get_reaction_names(self) -> list[str]: #Unschön, sollte set geben
        names = []
        for reaction in self.reactions:
            names.append(reaction.name)
        return names
    
    def compute_mentioned_foods(self, foods:list[MoleculeType]) -> set[MoleculeType]:
        """Might need to return a dict?

        Args:
            foods (iter[MoleculeType]): foods to compare reactions against

        Returns:
            set[MoleculeType]: set of all MoleculeTypes mentioned in any reaction and foods
        """
        molecule_types = []
        for reaction in self.reactions:
            molecule_types.extend(reaction.reactants)
            molecule_types.extend(reaction.inhibitions)
            molecule_types.extend(reaction.products)
            molecule_types.extend(reaction.get_catalyst_elements()) #FEHLERANFÄLLIG, ursprünglich durch get_catalyst_conjunctions
        all_molecules_mentioned = set(molecule_types)
        return all_molecules_mentioned.intersection(foods)
    
    def replace_named_reaction(self, name:str, reaction:Reaction) -> None:
        old_reaction = self.get_reaction(name)
        if old_reaction == None:
            raise TypeError("no such reaction: " + name)
        self.reactions.remove(old_reaction)
        self.reactions.append(reaction)
        
    def sorted_by_hashcode(self) -> ReactionSystem:
        sorted_reaction_system = ReactionSystem(self.name)
        sorted_reaction_system.foods = sorted(self.foods)
        sorted_reaction_system.reactions = sorted(self.reactions)
        return sorted_reaction_system
    
    def get_reaction(self, name:str) -> Reaction:
        for reaction in self.reactions: #UNSCHÖN
            if reaction.name == name: return reaction
    
    #ENTERNT, Properties selbst müssen via self.xx angesteuert werden
    
    def get_number_of_one_way_reactions(self) -> int:
        return self.size - self.number_of_two_way_reactions
    
    def __eq__(self, other:ReactionSystem) -> bool:
        if hash(self) == hash(other): return True #FEHLERANFÄLLIG, temporäre Lösung
        if not (isinstance(other, ReactionSystem)): return False
        return (set(self.foods) == set(other.foods) 
                and set(self.reactions) == set(other.reactions))
        
    def __lt__(self, other:Reaction) -> bool:
        return hash(self) < hash(other)
    
    def __hash__(self) -> int:
        return hash((tuple(self.foods), tuple(self.reactions)))