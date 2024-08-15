from __future__ import annotations

import copy
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from sample.model.ReactionSystem import ReactionSystem
from sample.model.Reaction import Reaction
from sample.algorithm.IDescribed import IDescribed
from sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
from sample.algorithm.MaxCAFAlgorithm import MaxCAFAlgorithm

class GreedilyGrowMaxCAF2MaxRAF(IDescribed):


    @property
    def description(self):
        return "greedily grow maxCAF to maxRAF by making reactions spontaneous"
    
    def apply(input_reaction_system:ReactionSystem) -> None:
        max_caf = MaxCAFAlgorithm().apply(input_reaction_system)
        max_raf = MaxRAFAlgorithm().apply(input_reaction_system)

        remaining_reactions = [r for r in max_raf.reactions if not (r.name in max_caf.get_reaction_names())]
        
        augmented_reactions = []
        augmented_system = copy.copy(max_raf)
        augmented_caf_size = max_caf.size

        while(augmented_caf_size < max_raf.size):
            best:tuple[Reaction, int] = ()
            cache = []
            for name in remaining_reactions:
                cache.append(GreedilyGrowMaxCAF2MaxRAF.apply_best_finder_helper(name, max_raf, augmented_system))
            best = max(cache, key=lambda x: x[1])

            if best != ():
                augmented_reaction = best[0]
                augmented_caf_size = best[1]
                augmented_system.replace_named_reaction(augmented_reaction.name, augmented_reaction)

                augmented_reactions.append(augmented_reaction.name)
                remaining_reactions.remove(augmented_reaction.name)
            else:
                print("No valid greedy choice found") #UNSCHÖN, sollte in Error Window(?) laufen
        
        result = (max_caf.size, max_raf.size, augmented_reactions)
        message = ""

        if len(result[2]) == 0 and result[0] == result[1]:
            message = "Greedily grow MaxCAF to MaxRAF: no reactions required to be spontaneous, because MaxCAF=MaxRAF"
        else:
            message = "Greedily grow MaxCAF (size " + result[0] +  ") to MaxRAF (size " + result[1] +  "): required %d reactions to be spontaneous: %s" #UNKLAR, was wird wieder gegeben


    def apply_best_finder_helper(reaction_name:str, max_raf:ReactionSystem, augmented_system:ReactionSystem) -> tuple[Reaction, int]:
        augmented_reaction:Reaction = copy.deepcopy(max_raf.get_reaction)
        augmented_reaction.catalysts = ""
        augmented_reaction.inhibitions.clear

        working_system = copy.copy(augmented_system)
        working_system.replace_named_reaction(reaction_name, augmented_reaction)
        
        working_max_caf:ReactionSystem = MaxCAFAlgorithm.apply(working_system)
        return (augmented_reaction, working_max_caf.size)