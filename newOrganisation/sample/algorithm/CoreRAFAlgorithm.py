from __future__ import annotations
from sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
from sample.algorithm.Importance import Importance
from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.model.ReactionSystem import ReactionSystem
from tqdm import tqdm

import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


class CoreRAFAlgorithm (AlgorithmBase):
    '''
    Computes the unique, irreducible RAF if it exists.
    '''
    NAME: str = "Core RAF"

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def description(self):
        return "computes the unique irreducible RAF, if it exists (Section 4.1 of [SXH20])"

    def apply(self, input: ReactionSystem) -> ReactionSystem:
        """Computes the unique, irreducible RAF if it exists.

        Args:
            input (ReactionSystem): reaction system to reduce

        Returns:
            ReactionSystem: core raf
        """
        max_raf = MaxRAFAlgorithm().apply(input)
        with tqdm(total=max_raf.size, desc="CoreRAFAlgorithm") as craf_pbar:

            important_reactions = ReactionSystem("Important")
            important_reactions.reactions = [p[0] for p in Importance.compute_reaction_importance(
                input, max_raf, MaxRAFAlgorithm, craf_pbar) if p[1] == 100.0]
            important_reactions.foods = list(
                important_reactions.compute_mentioned_foods(input.foods))

            core_raf = MaxRAFAlgorithm().apply(important_reactions)
            core_raf.name = "Core RAF"
            craf_pbar.update(1)
        return core_raf
