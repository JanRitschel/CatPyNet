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
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from sample.model.ReactionSystem import ReactionSystem
from sample.algorithm.IDescribed import IDescribed


class AlgorithmBase(IDescribed):
    '''
    computes a new reaction system
    Daniel Huson, 7.2019
    '''
    """ def __init__(self):
        pass """
    
    NAME:str = ""
    
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
    
    # Version with all vars
    # def apply(input:ReactionSystem, progress:ProgressListener) -> ReactionSystem: # throws CanceledException
    def apply(input:ReactionSystem) -> ReactionSystem: # throws CanceledException
        '''
        run the algorithm
        
        return output
        '''
        
        pass
    
    # Version with all vars
    # def listAllAlgorithms() -> Collection<String> :
    def list_all_algorithms() -> list[str] :
        '''
        list all known algorithms
        
        return names of all known algorithms
        '''
        list = []
        try:
            from sample.algorithm.CoreRAFAlgorithm import CoreRAFAlgorithm
            from sample.algorithm.MaxCAFAlgorithm import MaxCAFAlgorithm
            from sample.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
            from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
        except: pass
        for algorithm in AlgorithmBase.__subclasses__():
            list.append(algorithm.NAME)

        return list
    
    # def getAlgorithmByName(name:str) -> AlgorithmBase:
    def get_algorithm_by_name(name:str):
        '''
        get algorithm by name
        
        param name
        returns algorithm
        '''
        for algorithm in AlgorithmBase.__subclasses__():
            if name.casefold() == algorithm.NAME.casefold():
                return algorithm
            
        return None
