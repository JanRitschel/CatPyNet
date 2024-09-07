from sample.model.ReactionSystem import ReactionSystem
from sample.settings.ReactionNotation import ReactionNotation
from sample.settings.ArrowNotation import ArrowNotation
from sample.io.IOManager import redirect_to_writer, ALL_FILE_FORMATS, ModelIO
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from sample.algorithm.AlgorithmBase import AlgorithmBase
from tqdm import tqdm

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

ALL_ALGORITHMS = AlgorithmBase.list_all_algorithms()
ALL_ALGORITHMS.extend([algo.lower()
                      for algo in AlgorithmBase.list_all_algorithms()])


def parse_input_file(file_name: str) -> ReactionSystem:

    res_lines = []
    notation = {None, None}
    with open(file_name, "r") as f:
        res_lines = f.readlines()
        if not res_lines:
            raise IOError("Can't read file: " + file_name)
        notation = ReactionNotation.detect_notation(res_lines)
        if notation[0] == None:
            raise IOError(
                "Can't detect 'full', 'sparse' or 'tabbed' file format.")
        res_reactiosystem = ReactionSystem()
        leading_comments = ModelIO.read(
            res_reactiosystem, file_name, notation[0])

        twr_str = "(" + str(res_reactiosystem.number_of_two_way_reactions) + \
            " two-way)" if res_reactiosystem.number_of_two_way_reactions > 0 else ""
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

def apply_algorithm(input_system:ReactionSystem,
                    algorithm:AlgorithmBase,
                    heuristic_runs:int = 10):
    
    if algorithm == MinIRAFHeuristic:
        irr_raf_heuristic = MinIRAFHeuristic()
        irr_raf_heuristic.number_of_random_insertion_orders = heuristic_runs
        output_systems = irr_raf_heuristic.apply_all_smallest(input_system)
    else:
        output_system = algorithm().apply(input_system)
        output_systems = [output_system]
    
    return output_systems

def run_on_file(algorithm:str|AlgorithmBase,
                  input_file:str,
                  output_path:str = "stdout",
                  zipped:str|bool = False,
                  output_format:str = ".crs",
                  reaction_notation:str|ReactionNotation = ReactionNotation.FULL,
                  arrow_notation:str|ArrowNotation = ArrowNotation.USES_EQUALS,
                  heuristic_runs:str|int = 10):
    
    input_system = parse_input_file(input_file)
    
    if isinstance(zipped, str):
        zipped = zipped.casefold()
        zipped = True if zipped == "True".casefold() else False
    
    if not isinstance(algorithm, AlgorithmBase) and isinstance(algorithm, str):
        algorithm: AlgorithmBase = AlgorithmBase.get_algorithm_by_name(algorithm)

    if isinstance(heuristic_runs, str):
        heuristic_runs = int(heuristic_runs)
    
    output_systems = apply_algorithm(input_system, algorithm, heuristic_runs)
    
    redirect_to_writer(output_systems, output_path, 
                       output_format, zipped, 
                       reaction_notation, arrow_notation,
                       algorithm)    
    
    tqdm.write("algo done")