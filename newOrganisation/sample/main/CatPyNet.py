from sample.model.ReactionSystem import ReactionSystem, MoleculeType, Reaction
from sample.settings.ReactionNotation import ReactionNotation
from sample.settings.ArrowNotation import ArrowNotation
from sample.io.IOManager import redirect_to_writer, ALL_FILE_FORMATS, ModelIO
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from sample.algorithm.AlgorithmBase import AlgorithmBase
import sample.Utilities as Utilities
from itertools import combinations_with_replacement
import random
import bisect
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


def apply_algorithm(input_system: ReactionSystem,
                    algorithm: AlgorithmBase,
                    heuristic_runs: int = 10):

    if algorithm == MinIRAFHeuristic:
        irr_raf_heuristic = MinIRAFHeuristic()
        irr_raf_heuristic.number_of_random_insertion_orders = heuristic_runs
        output_system = irr_raf_heuristic.apply(input_system)
    else:
        output_system = algorithm().apply(input_system)
        output_system = output_system

    return output_system


def run_on_file(algorithm: str | AlgorithmBase,
                input_file: str,
                output_path: str = "stdout",
                zipped: str | bool = False,
                output_format: str = ".crs",
                reaction_notation: str | ReactionNotation = ReactionNotation.FULL,
                arrow_notation: str | ArrowNotation = ArrowNotation.USES_EQUALS,
                heuristic_runs: str | int = 10):

    input_system = parse_input_file(input_file)

    if isinstance(zipped, str):
        zipped = zipped.casefold()
        zipped = True if zipped == "True".casefold() else False

    if not isinstance(algorithm, AlgorithmBase) and isinstance(algorithm, str):
        algorithm: AlgorithmBase = AlgorithmBase.get_algorithm_by_name(
            algorithm)

    if isinstance(heuristic_runs, str):
        heuristic_runs = int(heuristic_runs)

    output_systems = apply_algorithm(input_system, algorithm, heuristic_runs)

    redirect_to_writer([output_systems], output_path,
                       output_format, zipped,
                       reaction_notation, arrow_notation,
                       algorithm)

    tqdm.write("algo done")


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
                                   arrow_notation: ArrowNotation = ArrowNotation.USES_EQUALS) -> None:
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

                            if all([x != None for x in parameters.values()]):
                                res_reaction_system = generate_reaction_system(
                                    parameters)
                            else:
                                res_reaction_system = None

                            if output_directory == "stdout":
                                filename = "stdout"
                            else:
                                file = Utilities.replace_parameters(
                                    file_template, parameters)
                                filename = os.path.join(output_directory, file)

                            redirect_to_writer([res_reaction_system], filename,
                                               output_format, zipped,
                                               arrow_notation, reaction_notation)

                            pbar.update(1)
                            files_count += 1
    tqdm.write("Number of files created: " + str(files_count))


def generate_reaction_system(parameters: dict[str:int, str:int, str:int, str:float, str:int]) -> ReactionSystem:

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
