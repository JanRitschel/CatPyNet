import argparse
import zipfile
from tqdm import tqdm

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from sample.io.ModelIO import ModelIO
from sample.settings.ArrowNotation import ArrowNotation
from sample.settings.ReactionNotation import ReactionNotation
from sample.model.ReactionSystem import ReactionSystem

def main():

    all_algorithms = AlgorithmBase.list_all_algorithms()
    all_algorithms.extend([algo.lower() for algo in AlgorithmBase.list_all_algorithms()])
    
    parser = argparse.ArgumentParser(description=
                                     "Performs Max RAF and other computations")
    
    parser.add_argument("--version", action="version", version='%(prog)s 1.0') #ZU MACHEN, Versionsnummer muss ordnetlich geklärt werden
    parser.add_argument("--license", action="store_const", 
                        const="Copyright (C) 2023. GPL 3. This program comes with ABSOLUTELY NO WARRANTY.") #ZU MACHEN, License muss richtige sein
    parser.add_argument("--authors", action="store_const", 
                        const="Daniel H. Huson and Mike Steel.") #ZU MACHEN, Autoren müssen richtige sein
    parser.add_argument("-c", metavar="compute", required=True, help="The computation to perform", choices= all_algorithms)
    parser.add_argument("-i", metavar="input", help="Input file (stdin ok)", default="stdin") #UNKLAR, soll der file so heißen oder wird etwas spezifisches aufgerufen
    parser.add_argument("-o", metavar='o', help="Output file (stdout ok)", default="stdout")
    parser.add_argument("-rn", metavar="reaction_notation", help="Output reaction notation", default="FULL")
    parser.add_argument("-an", metavar="arrow_notation", help="Output arrow notation", default="USES_EQUALS")
    parser.add_argument("-r", metavar="runs", help= "Number of randomized runs for " + MinIRAFHeuristic().name + " heuristic")
    parser.add_argument("-p", metavar="properties_file", default="") #ZU MACHEN, Default File muss erstellt werden

    #ZU MACHEN, comment argument (?) mit OTHER variable aus ArgsOptions
    arguments = vars(parser.parse_args())
    #ZU MACHEN, Files auf verschiedenheit, schreibbarkeit und existenz prüfen
    input_system = parse_input_file(arguments['i']) 
    algorithm:AlgorithmBase = AlgorithmBase.get_algorithm_by_name(arguments['c'])
    if algorithm == MinIRAFHeuristic:
        irr_raf_heuristic = MinIRAFHeuristic()
        irr_raf_heuristic.number_of_random_insertion_orders = arguments['r']
        output_systems = irr_raf_heuristic.apply_all_smallest(input_system)
        if arguments['o'] != "stdout":  #ZU MACHEN, wieder std stuff
            tqdm.write("Writing file: " + arguments['o'])
        try:
            if ".zip" in arguments['o']:
                with zipfile.ZipFile(arguments['o'], "w") as zip_arch:
                    res_str = ""
                    for output_system in output_systems:
                        res_str += ModelIO().write(output_system,
                                                   True, 
                                                   arguments['rn'],
                                                   arguments['an']) 
                        + "\n"
                    zip_arch.writestr(arguments['o'],res_str)
            else:
                with open(arguments['o'], "w") as f:
                    res_str = ""
                    for output_system in output_systems:
                        res_str += ModelIO().write(output_system,
                                                   True, 
                                                   arguments['rn'],
                                                   arguments['an']) 
                        res_str += "\n"
                    f.write(res_str)
        except KeyError: #UNKLAR, braucht es überhaupt ein try statement?
            pass
    else:
        output_system = algorithm().apply(input_system)
        if arguments['o'] != "stdout":  #ZU MACHEN, wieder std stuff
            tqdm.write("Writing file: " + arguments['o'])
        try:
            if ".zip" in arguments['o']:
                with zipfile.ZipFile(arguments['o'], "w") as zip_arch:
                    res_str = ""
                    res_str += ModelIO().write(output_system,
                                                True, 
                                                arguments['rn'],
                                                arguments['an']) 
                    zip_arch.writestr(arguments['o'],res_str)
            else:
                with open(arguments['o'], "w") as f:
                    res_str = ""
                    res_str += ModelIO().write(output_system,
                                                True, 
                                                arguments['rn'],
                                                arguments['an']) 
                    f.write(res_str)
        except: #UNKLAR, braucht es überhaupt ein try statement?
            pass

def parse_input_file(file_name:str) -> ReactionSystem:
    
    #ZU MACHEN, ImportWimsFormat
    res_lines = []
    notation = {None,None}
    with open(file_name, "r") as f:
        res_lines = f.readlines()
        if not res_lines: raise IOError("Can't read file: " + file_name)
        notation = ReactionNotation.detect_notation(res_lines)
        if notation[0] == None: raise IOError("Can't detect 'full', 'sparse' or 'tabbed' file format.")
        res_reactiosystem = ReactionSystem()
        leading_comments = ModelIO.read(res_reactiosystem, file_name, notation[0])
        
        twr_str = "(" + str(res_reactiosystem.number_of_two_way_reactions) + " two-way)" if res_reactiosystem.number_of_two_way_reactions > 0 else ""
        output_str = ("Read " + str(res_reactiosystem.size) + " reactions " + 
                      twr_str + " and " + str(res_reactiosystem.food_size) + 
                      " food items from file: " + file_name)
        if not leading_comments == "":
            output_str += "\n Comments:\n" + str(leading_comments)
        res_reactiosystem.update_inhibitors_present()
        if res_reactiosystem.inhibitors_present:
            output_str += "Input catalytic reaction system contains inhibitions. These are ignored in the computation of maxCAF, maxRAF and maxPseudoRAF"
            
        tqdm.write(output_str)

    return res_reactiosystem

if __name__ == "__main__":
    main()