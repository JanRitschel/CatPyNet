from __future__ import annotations
from catpynet.algorithm.AlgorithmBase import AlgorithmBase
from catpynet.model.MoleculeType import MoleculeType
from catpynet.model.Reaction import Reaction
from catpynet.model.ReactionSystem import ReactionSystem
import time
from tqdm import tqdm

import copy
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class Importance ():

    def get_description() -> str:
        return "computes the percent difference between model size and model size without given food item [HS23]"

    def compute_food_importance(input_system: ReactionSystem,
                                original_result: ReactionSystem,
                                algorithm: AlgorithmBase) -> list[tuple[MoleculeType, float]]:
        """Calculates importance of one molecule in food for reaction system size.

        Args:
            input_system (ReactionSystem): system to be analyzed
            original_result (ReactionSystem): original result of algorithm on input system
            algorithm (AlgorithmBase): algorithm to be used on input system

        Returns:
            list[tuple[MoleculeType, float]]: list of importances of food molecules from (0, 100].
            
        Food items are only listed if they have any importance. If they can be ignored with the same result they are not listed.
        """        
        result = []
        for food in input_system.foods:
            replicate_input = copy.copy(input_system)
            replicate_input.name = "Food importance"
            replicate_input.foods.remove(food)

            replicate_output = algorithm().apply(replicate_input)
            importance = 100.0 * \
                (original_result.size - replicate_output.size) / \
                float(original_result.size)
            if importance > 0:
                result.append((food, importance))
            result.sort(lambda x: x[1])
        return result

    def compute_reaction_importance(input_system: ReactionSystem,
                                    original_result: ReactionSystem,
                                    algorithm: AlgorithmBase,
                                    pbar: tqdm) -> list[tuple[Reaction, float]]:
        """Calculates importance of one reacton for reaction system size.

        Args:
            input_system (ReactionSystem): system to be analyzed
            original_result (ReactionSystem): original result of algorithm on input system
            algorithm (AlgorithmBase): algorithm to be used on input system

        Returns:
            list[tuple[MoleculeType, float]]: list of importances of reactions from (0, 100].
            
        Reaction items are only listed if they have any importance. If they can be ignored with the same result they are not listed.
        """          
        result = []
        if original_result.size == 1:
            result.append((original_result.reactions[0], 100.0))
        elif original_result.size > 1:
            size_to_compare_against = original_result.size - 1
            replicate_input = ReactionSystem("Reaction importance")
            replicate_input.foods = input_system.foods
            replicate_input.reactions = input_system.reactions.copy()
            for reaction in tqdm(input_system.reactions, desc="Calculating Reaction Importance: "):
                replicate_input.reactions.remove(reaction)

                replicate_output: ReactionSystem = algorithm().apply(replicate_input)
                if replicate_output.size < size_to_compare_against:
                    importance = (100.0 * 
                        (size_to_compare_against - replicate_output.size) / 
                        float(size_to_compare_against))
                    if importance > 0:
                        result.append((reaction, importance))
                replicate_input.reactions.append(reaction)
                pbar.update(1)
            result.sort(key=lambda x: x[1])
        return result

    def to_string_food_importance(food_imortance: list[tuple[MoleculeType, float]]) -> str:
        buffer = ""
        buffer += "Food importance: "
        first = True
        for pair in food_imortance:
            if first:
                first = False
            else:
                buffer += ", "
            buffer += pair[0].name + " " + str(pair[1])

        return buffer

    def to_string_reaction_importance(reaction_imortance: list[tuple[MoleculeType, float]]) -> str:
        buffer = ""
        buffer += "Reaction importance: "
        first = True
        for pair in reaction_imortance:
            if first:
                first = False
            else:
                buffer += ", "
            buffer += pair[0].name + " " + str(pair[1])

        return buffer
