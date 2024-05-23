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

from ..model.ReactionSystem import ReactionSystem
from .IDescribed import IDescribed
# Java modules to find replacements for
'''
import jloda.util.CanceledException
import jloda.util.PluginClassLoader
import jloda.util.StringUtils
import jloda.util.progress.ProgressListener

import java.util.ArrayList
import java.util.Collection
'''

class AlgorithmBase(IDescribed):
    '''
    computes a new reaction system
    Daniel Huson, 7.2019
    '''
    """ 
    def __init__():
        pass """
    
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
        for algorithm in AlgorithmBase.__subclasses__():
            list.append(algorithm.getName().title())

        return list
    
    # def getAlgorithmByName(name:str) -> AlgorithmBase:
    def get_algorithm_by_name(name:str):
        '''
        get algorithm by name
        
        param name
        returns algorithm
        '''
        for algorithm in AlgorithmBase.__subclasses__():
            if name.casefold() == algorithm.getName().casefold():
                return algorithm
            
        return None
