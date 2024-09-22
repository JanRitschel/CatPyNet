from model.ReactionSystem import ReactionSystem, MoleculeType, Reaction
from settings.ReactionNotation import ReactionNotation
from settings.ArrowNotation import ArrowNotation
from fileIO.IOManager import redirect_to_writer, OUTPUT_FILE_FORMATS, INPUT_FILE_FORMATS, ModelIO
from algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from algorithm.MinRAFGeneratingElement import MinRAFGeneratingElement
from algorithm.AlgorithmBase import AlgorithmBase
import Utilities as Utilities
from itertools import combinations_with_replacement
import shutil
import random
import bisect
from tqdm import tqdm

from time import time

from os.path import isfile, join, isdir
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

ALL_ALGORITHMS = AlgorithmBase.list_all_algorithms()
ALL_ALGORITHMS.update([algo.lower()
                      for algo in AlgorithmBase.list_all_algorithms()])


def parse_input_file_to_rs(file_name: str) -> ReactionSystem:
    """Builds a ReactionSystem from a .crs-file

    Args:
        file_name (str): absolute path to .crs-file

    Raises:
        IOError: Wrong file Format
        IOError: Can't read file
        IOError: Can't detect format

    Returns:
        ReactionSystem: ReactionSystem equivalent to input_file
    """    
    res_lines = []
    notation = [None, None]
    if os.path.splitext(file_name)[1] not in INPUT_FILE_FORMATS:
        raise IOError("The file format " + os.path.splitext(file_name)[1] 
                      + " is not supported by this function.\n"
                      + "Please try a file with format in: " +
                      str(INPUT_FILE_FORMATS))
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


def export_rs_to_output_file(output_systems:list[ReactionSystem],
                       output_path:str ="stdout",
                       output_format:str|None = None,
                       zipped:bool = False, 
                       reaction_notation:str = ReactionNotation.FULL,
                       arrow_notation:str = ArrowNotation.USES_EQUALS,
                       algorithm:AlgorithmBase|None = None):
    """export Reactionsystems as output_format-files

    Args:
        output_systems (list[ReactionSystem]): reaction systems to be written as a file/files
        output_path (str, optional): path to generated file. Default stdout prints in terminal. Defaults to "stdout".
        output_format (str | None, optional): If given this determines the file format of the output. Defaults to None.
        zipped (bool, optional): should the resulting files be zipped to an archive. Defaults to False.
        reaction_notation (str, optional): For '.crs' files. Determines reaction notation format. Defaults to ReactionNotation.FULL.
        arrow_notation (str, optional): For '.crs' files. Determines arrow format. Defaults to ArrowNotation.USES_EQUALS.
        algorithm (AlgorithmBase | None, optional): only relevant for message generation. Defaults to None.
    """
    redirect_to_writer(output_systems,
                       output_path,
                       output_format,
                       zipped, 
                       reaction_notation,
                       arrow_notation,
                       algorithm)


def apply_algorithm_to_rs(input_system: ReactionSystem,
                    algorithm: AlgorithmBase,
                    heuristic_runs: int = 10,
                    target_molecule:list[str] = []) -> ReactionSystem|None:
    """Applies the given algorithm to the input_system and returns the result.

    Args:
        input_system (ReactionSystem): system to find autocatalytic system in
        algorithm (AlgorithmBase): algorithm of autocatalytic system to find
        heuristic_runs (int, optional): number of seeds to check if algorithm is heuristic. Defaults to 10.
        target_molecule (list[str], optional): names of molecules to search for if algorithm has target. Defaults to [].

    Returns:
        ReactioSystem: autocatalytic ReactionSystem of given algorithm
    """    
    if isinstance(algorithm, MinIRAFHeuristic):
        algorithm.number_of_random_insertion_orders = heuristic_runs
        output_system = algorithm.apply(input_system)
    elif isinstance(algorithm, MinRAFGeneratingElement):
        algorithm.targets = MoleculeType().values_of(target_molecule)
        algorithm.number_of_random_insertion_orders = heuristic_runs
        output_system = algorithm.apply(input_system)
    else:
        output_system = algorithm.apply(input_system)

    return output_system


def apply_algorithm_to_file(algorithm: str | AlgorithmBase,
                  input_file: str,
                  output_path: str = "stdout",
                  zipped: bool = False,
                  output_format: str = ".crs",
                  reaction_notation: str | ReactionNotation = ReactionNotation.FULL,
                  arrow_notation: str | ArrowNotation = ArrowNotation.USES_EQUALS,
                  heuristic_runs: str | int = 10,
                  target_molecule:list[str] = [],
                  overwrite_ok: bool = False) -> ReactionSystem|None:
    """Applies the given algorithm to the input system, returns the result and writes it as a file at output_path.

    Args:
        algorithm (str | AlgorithmBase): (name of) algorithm of autocatalytic system to find
        input_file (str): path to .crs file to find autocatalytic system in
        output_path (str, optional): path to write resulting system to. Defaults to "stdout".
        zipped (bool, optional): Should the resulting file be zipped. Defaults to False.
        output_format (str, optional): file format of the output path. Overwrites output_file ending. Defaults to ".crs".
        reaction_notation (str | ReactionNotation, optional): Reaction format from FULL, SPARSE, TABBED. Defaults to ReactionNotation.FULL.
        arrow_notation (str | ArrowNotation, optional): Arrow format from USES_EQUALS, USES_MINUS. Defaults to ArrowNotation.USES_EQUALS.
        heuristic_runs (str | int, optional): number of seeds to check if algorithm is heuristic. Defaults to 10.
        target_molecule (list[str], optional): names of molecules to search for if algorithm has target. Defaults to [].
        overwrite_ok (bool, optional): Is the function allowed to write over existing files. Defaults to False.

    Returns:
        ReactionSystem|None: autocatalytic ReactionSystem of given algorithm
    """    
    start_time = time()
    input_system = parse_input_file_to_rs(input_file)

    if not overwrite_ok and os.path.exists(output_path):
        tqdm.write("The given output file " + output_path + " already exists.\n"
                   + "If you want to overwrite it please run this function with "
                   + "the 'overwrite_ok' attribute set to True")
        return

    if isinstance(algorithm, str):
        algorithm: AlgorithmBase = AlgorithmBase.get_algorithm_by_name(
            algorithm)
    
    if isinstance(algorithm, type): algorithm = algorithm()
    
    if isinstance(heuristic_runs, str):
        heuristic_runs = int(heuristic_runs)

    output_systems = apply_algorithm_to_rs(input_system, algorithm, heuristic_runs, target_molecule)

    redirect_to_writer([output_systems], output_path,
                       output_format, zipped,
                       reaction_notation, arrow_notation,
                       algorithm)
    
    tqdm.write("Total time spent: " + str(time() - start_time))
    return output_systems


def apply_algorithm_to_directory(algorithm: str | AlgorithmBase,
                       input_directory: str,
                       output_path: str = "stdout",
                       zipped: bool = False,
                       output_format: str = ".crs",
                       reaction_notation: str | ReactionNotation = ReactionNotation.FULL,
                       arrow_notation: str | ArrowNotation = ArrowNotation.USES_EQUALS,
                       heuristic_runs: str | int = 10,
                       target_molecule:list[str] = [],
                       overwrite_ok: bool = False,
                       time_dict:dict = {}) -> list[ReactionSystem]|None:
    """Applies the given algorithm to the input systems, returns the result and writes it as a file at output_path.

    Args:
        algorithm (str | AlgorithmBase): (name of) algorithm of autocatalytic system to find
        input_directory (str): path to directory to find autocatalytic systems in. Consumes all .crs files in the directory.
        output_path (str, optional): path to write resulting systems to. Defaults to "stdout".
        zipped (bool, optional): Should the resulting file be zipped. Defaults to False.
        output_format (str, optional): file format of the output path. Overwrites output_file ending. Defaults to ".crs".
        reaction_notation (str | ReactionNotation, optional): Reaction format from FULL, SPARSE, TABBED. Defaults to ReactionNotation.FULL.
        arrow_notation (str | ArrowNotation, optional): Arrow format from USES_EQUALS, USES_MINUS. Defaults to ArrowNotation.USES_EQUALS.
        heuristic_runs (str | int, optional): number of seeds to check if algorithm is heuristic. Defaults to 10.
        target_molecule (list[str], optional): names of molecules to search for if algorithm has target. Defaults to [].
        overwrite_ok (bool, optional): Is the function allowed to write over existing files. Defaults to False.

    Returns:
        list[ReactionSystem]|None: A list of all ReactionSystems created this way
    """    
    
    st = time()
    if os.path.splitext(output_path)[1]:
        output_path = os.path.splitext(output_path)[0]
    
    if output_format not in OUTPUT_FILE_FORMATS or not output_format:
        tqdm.write("please choose a valid file format from:\n" +
                   str(OUTPUT_FILE_FORMATS) + "\n"+
                   "File format cannot be inferred here.")
        return
    
    dir_files = [join(input_directory, f) for f in os.listdir(input_directory)
                 if isfile(join(input_directory, f))]

    file_zipped = False
    output_systems=[]
    for file in tqdm(dir_files, desc="Files to " + output_path):
        if os.path.splitext(file)[1] in INPUT_FILE_FORMATS:
            if isdir(output_path) or output_path == 'stdout':
                output_file = os.path.join(output_path, os.path.split(file)[1])
                output_systems.append(apply_algorithm_to_file(algorithm, file, output_file, file_zipped, output_format,
                              reaction_notation, arrow_notation, heuristic_runs, target_molecule, overwrite_ok))
            else:
                os.makedirs(output_path, exist_ok=True)
                output_file = os.path.join(output_path, os.path.split(file)[1])
                output_systems.append(apply_algorithm_to_file(algorithm, file, output_file, file_zipped, output_format,
                              reaction_notation, arrow_notation, heuristic_runs, target_molecule, overwrite_ok))
                
    if output_path != 'stdout' and zipped:
        shutil.make_archive(output_path, 'zip', output_path)
        if os.path.isdir(output_path):
            shutil.rmtree(output_path)
    et = time()
    time_dict.update({output_path:et-st})
    return output_systems


def generate_reaction_system_files(alphabet_sizes: list[int],
                                   food_max_lengths: list[int],
                                   polymer_max_lengths: list[int],
                                   means: list[float],
                                   number_of_replicates: int,
                                   output_directory: str = 'stdout',
                                   file_template: str = "polymer_model_a#a_k#k_n#n_m#m_r#r.crs",
                                   zipped: bool = False,
                                   output_format: str = '.crs',
                                   reaction_notation: ReactionNotation = ReactionNotation.FULL,
                                   arrow_notation: ArrowNotation = ArrowNotation.USES_EQUALS,
                                   overwrite_ok: bool = False) -> None:
    """Generates .crs files of random polymer systems given input constraints.

    Args:
        alphabet_sizes (list[int]): number of unique minimal elements. only supports < 11
        food_max_lengths (list[int]): maximum number of elements a food molecule may consist of
        polymer_max_lengths (list[int]): maximum number of elements any polymer molecule may consist of
        means (list[float]): mean number of reactions a polymer catalyzes
        number_of_replicates (int): seed for replication
        output_directory (str, optional): directory to write output systems into. Defaults to 'stdout'.
        file_template (str, optional): template for single files in dorectories. Defaults to "polymer_model_a#a_k#k_n#n_m#m_r#r.crs".
        zipped (bool, optional): should the resulting directory be zipped. Defaults to False.
        output_format (str, optional): file format of the output path. Overwrites file_template ending. Defaults to '.crs'.
        reaction_notation (ReactionNotation, optional): Reaction format from FULL, SPARSE, TABBED. Defaults to ReactionNotation.FULL.
        arrow_notation (ArrowNotation, optional): Arrow format from USES_EQUALS, USES_MINUS. Defaults to ArrowNotation.USES_EQUALS.
        overwrite_ok (bool, optional): Is the function allowed to write over existing files. Defaults to False.
    
    In the file template replacement works as follows:
        - "#a": alphabet_size
        - "#k": food_max_length
        - "#n": polymer_max_length
        - "#m": mean
        - "#r": number_of_replicates
    """    

    tqdm.write("writing files to: " + output_directory)
    
    files_count = 0
    total_files_expected = len(alphabet_sizes) * len(food_max_lengths) * len(
        polymer_max_lengths) * len(means) * len(number_of_replicates)
    with tqdm(total=total_files_expected, desc="Files: ") as pbar:
        for a in alphabet_sizes:
            for k in food_max_lengths:
                for n in polymer_max_lengths:
                    for m in means:
                        for r in number_of_replicates:

                            parameters = {"a": a, "k": k,
                                          "n": n, "m": m, "r": r}

                            if output_directory == "stdout":
                                filename = "stdout"
                            else:
                                file = Utilities.replace_parameters(
                                    file_template, parameters)
                                filename = os.path.join(output_directory, file)

                            if os.path.exists(filename) and not overwrite_ok:
                                tqdm.write("The given output file " + filename + " already exists.\n"
                                           + "If you want to overwrite it please run this function with "
                                           + "the 'overwrite_ok' attribute set to True")
                                continue

                            if all([x != None for x in parameters.values()]):
                                res_reaction_system = generate_reaction_system(
                                    parameters)
                            else:
                                tqdm.write(
                                    "Not all neccessary paramters were given.\n")
                                for key, value in zip(parameters.keys(), parameters.values()):
                                    if not value:
                                        tqdm.write("- missing: " + key)
                                return

                            redirect_to_writer([res_reaction_system], filename,
                                               output_format, zipped,
                                               arrow_notation, reaction_notation)

                            pbar.update(1)
                            files_count += 1
    tqdm.write("Number of files created: " + str(files_count))


def generate_reaction_system(parameters: dict[str:int, str:int, str:int, str:float, str:int]) -> ReactionSystem:
    """Generates a single random polymer reaction system given parameters

    Args:
        parameters (dict[str:int|float]): parameters of single random polymer system

    Returns:
        ReactionSystem: resulting reaction system.
        
    Parameters must include:
        - "a": alphabet_size (int)
        - "k": food_max_length (int)
        - "n": polymer_max_length (int)
        - "m": mean (float)
        - "r": number_of_replicates (int)
    """
    res_reaction_system = ReactionSystem(Utilities.replace_parameters(
        "# Polymer model a=#a k=#k n=#n m=#m r=#r", parameters))
    basic_elements = ["a" + str(i) for i in range(int(parameters["a"]))]
    food_names_lists = []
    for k in tqdm(range(1, int(parameters["k"]) + 1),
                  desc=res_reaction_system.name + " Foods Generation: "):
        food_names_lists.extend(
            list(combinations_with_replacement(basic_elements, k)))
    food_names: list[str] = ["".join(fl) for fl in food_names_lists]
    res_reaction_system.foods = MoleculeType().values_of(food_names)

    polymer_names_lists = []
    for n in tqdm(range(1, int(parameters["n"]) + 1),
                  desc=res_reaction_system.name + " Polymer Generation: "):
        polymer_names_lists.extend(
            list(combinations_with_replacement(basic_elements, n)))
    polymers: list[str] = ["".join(pl) for pl in polymer_names_lists]
    estimate_n_reactions = 0
    for polymer in polymers:
        estimate_n_reactions += len(polymer) / 2
    digits_estimate = len(str(int(estimate_n_reactions)))

    reactions = []
    count = 0
    with tqdm(desc=res_reaction_system.name + " Reaction Generation ",
              total=estimate_n_reactions) as r_pbar:
        for polymer in polymers:
            for i in range(0, len(polymer), 2):
                r_pbar.update(1)
                count += 1
                reaction = Reaction("r" + str(count).zfill(digits_estimate))
                if i == 0:
                    continue
                prefix = polymer[0:i]
                suffix = polymer[i:]
                reaction.reactants = MoleculeType().values_of([prefix, suffix])
                reaction.products = MoleculeType().values_of([polymer])
                reaction.direction = Reaction().DIRECTION["both"]
                reactions.append(reaction)

    reaction_length = len(reactions)
    p = parameters["m"]/reaction_length
    if p > 1:
        tqdm.write(
            "This mean: "
            + parameters["m"]
            + "\nis impossible to achieve since there are fewer possible reactions than the mean.")
        p = 1.0
    elif p < 0:
        tqdm.write(
            "This mean: "
            + parameters["m"]
            + "\nis impossible to achieve since it is negative.")
    dist = Utilities.binom_dist(
        reaction_length,  parameters["m"]/reaction_length)
    random.seed = parameters["r"]
    for polymer in polymers:
        successes = bisect.bisect_right(
            dist, random.uniform(0, 0.999999999999))
        i = 0
        while i < successes:
            reaction: Reaction = reactions[random.randint(
                0, reaction_length - 1)]
            if polymer in reaction.catalysts:
                continue
            if reaction.catalysts.strip() == "":
                reaction.catalysts = polymer
            else:
                reaction.catalysts += "," + polymer
            i += 1

    for reaction in reactions:
        if reaction.catalysts.strip() != "":
            res_reaction_system.reactions.append(reaction)

    return res_reaction_system
