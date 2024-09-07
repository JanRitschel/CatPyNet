from sample.io.IOManager import ALL_FILE_FORMATS
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from sample.algorithm.AlgorithmBase import AlgorithmBase
import sample.main.CatPyNet as cpn
import argparse
from tqdm import tqdm

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

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
                        help="file format to be written. e.g. '.crs'", 
                        choices=ALL_FILE_FORMATS, 
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
    
    cpn.run_on_file(arguments['c'], arguments['i'], arguments['o'],arguments['z'], arguments['of'],
                    arguments['rn'], arguments['an'], arguments['r'])

if __name__ == "__main__":
    main()
