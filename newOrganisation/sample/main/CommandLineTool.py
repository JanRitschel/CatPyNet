from sample.model.ReactionSystem import ReactionSystem
from sample.settings.ReactionNotation import ReactionNotation
from sample.settings.ArrowNotation import ArrowNotation
from sample.io.GraphIO import write, SUPPORTED_GRAPH_FILE_FORMATS
from sample.io.ModelIO import ModelIO, SUPPORTED_FILE_FORMATS
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from sample.algorithm.AlgorithmBase import AlgorithmBase
import argparse
import shutil
from tqdm import tqdm

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


all_file_formats = SUPPORTED_FILE_FORMATS
all_file_formats.extend(SUPPORTED_GRAPH_FILE_FORMATS)
all_file_formats.extend([format.casefold() for format in all_file_formats])
all_file_formats.append(None)

all_algorithms = AlgorithmBase.list_all_algorithms()
all_algorithms.extend([algo.lower()
                      for algo in AlgorithmBase.list_all_algorithms()])


def main():

    parser = argparse.ArgumentParser(
        description="Performs Max RAF and other computations")

    # ZU MACHEN, Versionsnummer muss ordnetlich geklärt werden
    parser.add_argument("--version", action="version", version='%(prog)s 1.0')
    parser.add_argument("--license", action="store_const",
                        const="Copyright (C) 2023. GPL 3. This program comes with ABSOLUTELY NO WARRANTY.")  # ZU MACHEN, License muss richtige sein
    parser.add_argument("--authors", action="store_const",
                        const="Jan Ritschel")
    parser.add_argument("-c", metavar="compute", required=True,
                        help="The computation to perform", choices=all_algorithms)
    # UNKLAR, soll der file so heißen oder wird etwas spezifisches aufgerufen
    parser.add_argument("-i", metavar="input",
                        help="Input file (stdin ok)", default="stdin")
    parser.add_argument("-o", metavar='output_file',
                        help="Output file (stdout ok)", default="stdout")
    parser.add_argument("-z", metavar='output_zipped',
                        help="Should the output be a zipped directory. (True or False)", 
                        choices=["True", "False"], 
                        default="False")
    parser.add_argument("-of", metavar="output_format",
                        help="The file format to write to", 
                        choices=all_file_formats, 
                        default=None)
    parser.add_argument("-rn", metavar="reaction_notation",
                        help="Output reaction notation", default="FULL")
    parser.add_argument("-an", metavar="arrow_notation",
                        help="Output arrow notation", default="USES_EQUALS")
    parser.add_argument("-r", metavar="runs", help="Number of randomized runs for " +
                        MinIRAFHeuristic().name + " heuristic")
    # ZU MACHEN, Default File muss erstellt werden
    parser.add_argument("-p", metavar="properties_file", default="")

    arguments = vars(parser.parse_args())
    input_system = parse_input_file(arguments['i'])
    algorithm: AlgorithmBase = AlgorithmBase.get_algorithm_by_name(
        arguments['c'])
    output_path = arguments["o"]

    tqdm.write("parsed")

    if algorithm == MinIRAFHeuristic:
        irr_raf_heuristic = MinIRAFHeuristic()
        irr_raf_heuristic.number_of_random_insertion_orders = arguments['r']
        output_systems = irr_raf_heuristic.apply_all_smallest(input_system)
    else:
        output_system = algorithm().apply(input_system)
        output_systems = [output_system]

    tqdm.write("algo done")

    if not arguments['of'] and output_path != "stdout":
        arguments['of'] = os.path.splitext(output_path)[1]
    else:
        output_path = os.path.splitext(output_path)[0] + arguments['of']

    if arguments["z"] == "True":
        output = os.path.split(os.path.abspath(output_path))
        output_directory = os.path.join(output[0], output[1].split(".")[0])
        output_file = output[1]
        output_path = os.path.join(output_directory, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if arguments['o'] != "stdout":
        tqdm.write("Writing file: " + output_path)

    if arguments['of'] in SUPPORTED_GRAPH_FILE_FORMATS:
        write(output_systems, output_path)
    elif arguments['of'] == ".crs":
        with open(output_path, "w") as f:
            res_str = ""
            for output_system in output_systems:
                res_str += ModelIO().write(output_system,
                                           True,
                                           arguments['rn'],
                                           arguments['an'])
                res_str += "\n"
            f.write(res_str)
    elif output_path == "stdout":
        res_str = ""
        for output_system in output_systems:
            res_str += ModelIO().write(output_system,
                                       True,
                                       arguments['rn'],
                                       arguments['an'])
            res_str += "\n"
        print(res_str)
    else:
        tqdm.write("Given output file format was not recognized.\n" +
                   ".crs is assumed.")
        output_path = output_path.split(".")[0] + ".crs"
        with open(output_path, "w") as f:
            res_str = ""
            for output_system in output_systems:
                res_str += ModelIO().write(output_system,
                                           True,
                                           arguments['rn'],
                                           arguments['an'])
                res_str += "\n"
            f.write(res_str)

    tqdm.write("wrote file")

    if arguments['z'] == "True":
        shutil.make_archive(output_directory, 'zip', output_directory)
        if os.path.isdir(output_directory):
            shutil.rmtree(output_directory)

    tqdm.write("made zip")


def parse_input_file(file_name: str) -> ReactionSystem:

    # ZU MACHEN, ImportWimsFormat
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


if __name__ == "__main__":
    main()
