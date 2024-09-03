from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from tqdm import tqdm
import time

from sample.model.ReactionSystem import ReactionSystem

from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.algorithm.Importance import Importance
from sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm

class CoreRAFAlgorithm (AlgorithmBase):
    
    
    NAME:str = "Core RAF"
    
    @property
    def name(self) -> str:
        return self.NAME
    
    @property
    def description(self):
        return "computes the unique irreducible RAF, if it exists (Section 4.1 of [SXH20])"
    
    def apply(self, input:ReactionSystem) -> ReactionSystem:

        with tqdm(total= 2 + input.size) as craf_pbar:
            max_raf = MaxRAFAlgorithm().apply(input)
            craf_pbar.update(1)
            times = [time.time()]
            
            important_reactions = ReactionSystem("Important")
            important_reactions.reactions = [p[0] for p in Importance.compute_reaction_importance(input, max_raf, MaxRAFAlgorithm, craf_pbar, times) if p[1] == 100]
            tqdm.write(str(important_reactions.reactions))
            important_reactions.foods = list(important_reactions.compute_mentioned_foods(input.foods))
            tqdm.write(str(important_reactions.foods))
            
            core_raf = MaxRAFAlgorithm().apply(important_reactions)
            core_raf.name = "Core RAF"
            craf_pbar.update(1)
            times.append(time.time())
            tqdm.write(str(times))
        return core_raf