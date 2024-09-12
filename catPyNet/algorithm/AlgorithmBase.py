from __future__ import annotations
from model.ReactionSystem import ReactionSystem
'''
  AlgorithmBase.java Copyright (C) 2022 Daniel H. Huson
 
  (Some files contain contributions from other authors, who are then mentioned separately.)
 
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


class AlgorithmBase:
    '''
    computes a new reaction system.
    super class of all algorithms
    '''

    NAME: str = ""

    @property
    def name(self):
        pass

    @property
    def description(self):
        '''
        get the name of the reaction system computed by this algorithm

        returns name
        '''
        pass

    def apply(input: ReactionSystem) -> ReactionSystem:
        '''
        run the algorithm

        return output
        '''

        pass

    def load_algorithms():
        pass

    def list_all_algorithms() -> set[str]:
        '''
        list all known algorithms

        return names of all known algorithms
        '''
        list = []
        try:
            from algorithm.MaxPseudoRAFAlgorithm import MaxPseudoRAFAlgorithm
            from algorithm.CoreRAFAlgorithm import CoreRAFAlgorithm
            from algorithm.MaxCAFAlgorithm import MaxCAFAlgorithm
            from algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
            from algorithm.MinIRAFHeuristic import MinIRAFHeuristic
        except:
            pass
        for algorithm in AlgorithmBase.__subclasses__():
            list.append(algorithm.NAME)

        return set(list)

    def get_algorithm_by_name(name: str) -> AlgorithmBase | None:
        """gets a subclass of Algorithmbase by name

        Args:
            name (str): name of the searched algorithm

        Returns:
            AlgorithmBase | None: referenced algorithm
        """
        for algorithm in AlgorithmBase.__subclasses__():
            if name.casefold() == algorithm.NAME.casefold():
                return algorithm

        return None
