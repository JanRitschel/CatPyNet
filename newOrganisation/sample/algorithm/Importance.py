from __future__ import annotations
from sample.algorithm.IDescribed import IDescribed
from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.model.MoleculeType import MoleculeType
from sample.model.Reaction import Reaction
from sample.model.ReactionSystem import ReactionSystem
import time
from tqdm import tqdm

import copy
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


class Importance (IDescribed):

    def get_description() -> str:
        return "computes the percent difference between model size and model size without given food item [HS23]"

    def compute_food_importance(input_system: ReactionSystem,
                                original_result: ReactionSystem,
                                algorithm: AlgorithmBase) -> list[tuple[MoleculeType, float]]:
        result = []
        for food in input_system.foods:
            replicate_input = copy.copy(input_system)
            replicate_input.name = "Food importance"
            replicate_input.foods.remove(food)

            replicate_output = algorithm.apply(replicate_input)
            importance = 100.0 * \
                (original_result.size - replicate_output.get_size) / \
                float(original_result.size)
            if importance > 0:
                result.append((food, importance))
            result.sort(lambda x: x[1])
        return result

    def compute_reaction_importance(input_system: ReactionSystem,
                                    original_result: ReactionSystem,
                                    algorithm: AlgorithmBase,
                                    pbar: tqdm) -> list[tuple[Reaction, float]]:
        result = []
        if original_result.size == 1:
            result.append((original_result.reactions[0], 100.0))
        elif original_result.size > 1:
            size_to_compare_against = original_result.size - 1
            for reaction in input_system.reactions:
                replicate_input = copy.copy(input_system)
                replicate_input.name = "Reaction importance"
                replicate_input.reactions.remove(reaction)

                replicate_output: ReactionSystem = algorithm().apply(replicate_input)
                if replicate_output.size < size_to_compare_against:
                    importance = 100.0 * \
                        (size_to_compare_against - replicate_output.size) / \
                        float(size_to_compare_against)
                    if importance > 0:
                        result.append((reaction, importance))
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
