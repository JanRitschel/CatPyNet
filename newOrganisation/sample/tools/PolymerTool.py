from sample.Utilities import Utilities
from sample.model.ReactionSystem import ReactionSystem, MoleculeType, Reaction
from sample.io.ModelIO import ModelIO
from sample.io.IOManager import redirect_to_writer, ALL_FILE_FORMATS
import argparse
import zipfile
import random
import math
import bisect
import decimal
from tqdm import tqdm
from itertools import combinations_with_replacement

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


bin_times = {}


def main():

    parser = argparse.ArgumentParser(description="COnstructs Polymer Models")

    # ZU MACHEN, Versionsnummer muss ordnetlich geklärt werden
    parser.add_argument("--version", action="version", version='%(prog)s 1.0')
    parser.add_argument("--license", action="store_const",
                        const="Copyright (C) 2023. GPL 3. This program comes with ABSOLUTELY NO WARRANTY.")  # ZU MACHEN, License muss richtige sein
    parser.add_argument("--authors", action="store_const",
                        const="Daniel H. Huson and Mike Steel.")  # ZU MACHEN, Autoren müssen richtige sein
    parser.add_argument("-a", metavar="alphabet_size",
                        help="alphabet size (list (x,y,z,...) or range (x-z or x-z/step) ok)", 
                        default="2")
    parser.add_argument("-k", metavar="food_max_length",
                        help="food molecule max length  (list or range ok)", default="2")
    parser.add_argument("-n", metavar='polymer_max_length',
                        help="polymer max length  (list or range ok)", default="4")
    parser.add_argument("-m", metavar="mean_catalyzed",
                        help="mean number of catalyzed reactions per molecule  (list or range ok)", 
                        default="2.0")
    parser.add_argument("-r", metavar="replicate",
                        help="The replicate number/seed (list or range ok)", default="1")
    parser.add_argument("-o", metavar="output", help="Output directory (or stdout)",
                        default="stdout")
    parser.add_argument("-f", metavar="file_name_template",
                        help="file name template (use #a,#k,#n,#m,#r for parameters)", 
                        default="polymer_model_a#a_k#k_n#n_m#m_r#r.crs")
    parser.add_argument("-z", metavar='output_zipped',
                        help="Should the output be a zipped directory. (True or False)", 
                        choices=["True", "False"], 
                        default="False")
    parser.add_argument("-of", metavar="output_format",
                        help="file format to be written. e.g. '.crs'", 
                        choices=ALL_FILE_FORMATS, 
                        default=None)
    parser.add_argument("-rn", metavar="reaction_notation",
                        help="Output reaction notation", default="FULL")
    parser.add_argument("-an", metavar="arrow_notation",
                        help="Output arrow notation", default="USES_EQUALS")

    arguments = vars(parser.parse_args())

    alphabet_sizes = parse_integer_input(arguments["a"])
    food_max_legths = parse_integer_input(arguments["k"])
    polymer_max_lengths = parse_integer_input(arguments["n"])
    means = parse_float_input(arguments["m"])
    number_of_replicates = parse_integer_input(arguments["r"])
    tqdm.write("writing files to: " + arguments["o"])

    files_count = 0
    total_files_expected = len(alphabet_sizes) * len(food_max_legths) * len(
        polymer_max_lengths) * len(means) * len(number_of_replicates)
    with tqdm(total=total_files_expected, desc="Files: ") as pbar:
        for a in alphabet_sizes:
            for k in food_max_legths:
                for n in polymer_max_lengths:
                    for m in means:
                        for r in number_of_replicates:

                            parameters = {"a": a, "k": k,
                                          "n": n, "m": m, "r": r}

                            if all([x != None for x in parameters.values()]):
                                res_reaction_system = apply(parameters)
                            else:
                                res_reaction_system = None

                            if arguments["o"] == "stdout":
                                filename = "stdout"
                            else:
                                file = replace_parameters(
                                    arguments["f"], parameters)
                                filename = os.path.join(arguments["o"], file)
                            
                            redirect_to_writer([res_reaction_system], arguments['of'],
                                               arguments['z'], filename,
                                               arguments['an'], arguments["rn"])
                            
                            pbar.update(1)
                            files_count += 1
    tqdm.write("Number of files created: " + str(files_count))


def apply(parameters: dict[str:int, str:int, str:int, str:float, str:int]) -> ReactionSystem:

    res_reaction_system = ReactionSystem(replace_parameters(
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
    dist = binom_dist(reaction_length,  parameters["m"]/reaction_length)
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


def parse_float_input(input: str) -> list | range:

    if "," in input:
        output_ints = input.split(",")
        output_ints = [o.strip() for o in output_ints]
        output = []
        for o in output_ints:
            if Utilities.is_float(o) and not o.startswith("-", 0, 1):
                output.append(float(o))
    elif "-" in input:
        output = []
        if "/" in input:
            output_ints = [input.split(
                "-")[0]].extend(input.split("-")[1].split("/"))
            while output_ints[0] <= output_ints[1]:
                output.append(output_ints[0])
                output_ints[0] += output_ints[2]
        else:
            output_ints = input.split("-")
            while output_ints[0] <= output_ints[1]:
                output.append(output_ints[0])
                output_ints[0] += 1.0
    else:
        output = [(float(input) if not input.strip().startswith("-", 0, 1)
                  and Utilities.is_float(input.strip()) else None)]

    return output


def parse_integer_input(input: str) -> list | range:

    if "," in input:
        output_ints = input.split(",")
        output = []
        for o in output_ints:
            if o.strip().isdigit():
                output.append(int(o.strip()))
    elif "-" in input:
        if "/" in input:
            output_ints = [input.split(
                "-")[0]].extend(input.split("-")[1].split("/"))
            output = range(output_ints[0], output_ints[1], output_ints[2])
        else:
            output_ints = input.split("-")
            output = range(output_ints[0], output_ints[1])
    else:
        output = [int(input) if input.strip().isdigit() else None]

    return output


def replace_parameters(input_str: str, 
                       parameters: dict[str:int, str:int, str:int, str:float, str:int]) -> str:
    return (input_str.replace("#a", str(parameters["a"]))
            .replace("#k", str(parameters["k"]))
            .replace("#n", str(parameters["n"]))
            .replace("#m", str(parameters["m"]))
            .replace("#r", str(parameters["r"])))


def binom_dist(n: int, p: float) -> list[float]:

    dist = []
    p_of_eq_k = []
    for k in range(n+1):
        p_of_eq_k.append(decimal.Decimal(math.comb(n, k)) *
                         decimal.Decimal(p**k) * decimal.Decimal((1-p)**(n-k)))
        dist.append(sum(p_of_eq_k))
        if sum(p_of_eq_k) == sum(p_of_eq_k[:-1]):
            break 
    return dist


if __name__ == "__main__":
    main()
