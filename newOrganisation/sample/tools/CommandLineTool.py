from sample.io.IOManager import OUTPUT_FILE_FORMATS, TRUTH_STRINGS
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from tqdm import tqdm
import sample.main.CatPyNet as cpn
import argparse
import importlib.metadata

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


__version__ = importlib.metadata.version('catpynet')

def main():

    parser = argparse.ArgumentParser(
        description="Performs Max RAF and other computations")
    
    parser.add_argument("--version", action="version", version='%(prog)s ' + __version__)
    parser.add_argument("-c", metavar="compute", required=True,
                        help="The computation to perform", choices=cpn.ALL_ALGORITHMS)
    parser.add_argument("-i", metavar="input",
                        help="Input file (stdin ok)", default="stdin")
    parser.add_argument("-o", metavar='output_file',
                        help="Output file (stdout ok)", default="stdout")
    parser.add_argument("-z", metavar='output_zipped',
                        help="Should the output be a zipped directory. (True or False)", 
                        choices=TRUTH_STRINGS, 
                        default="False")
    parser.add_argument("-of", metavar="output_format",
                        help="file format to be written. e.g. '.crs'", 
                        choices=OUTPUT_FILE_FORMATS, 
                        default=None)
    parser.add_argument("-rn", metavar="reaction_notation",
                        help="Output reaction notation", default="FULL")
    parser.add_argument("-an", metavar="arrow_notation",
                        help="Output arrow notation", default="USES_EQUALS")
    parser.add_argument("-r", metavar="runs", help="Number of randomized runs for " +
                        MinIRAFHeuristic().name + " heuristic")
    parser.add_argument("-ow", metavar="overwrite ok", help="Sets if the program is allowed to " +
                        "write over files", choices=TRUTH_STRINGS, default="False")

    arguments = vars(parser.parse_args())
    zipped = True if arguments['z'].casefold() in ['True'.casefold(), "1"] else False
    overwrite_ok = True if arguments['ow'].casefold() in ['True'.casefold(), "1"] else False
    if arguments["i"] == 'stdin': 
        input_file = input("Please enter the file path you want to read from:")
    else:
        input_file = arguments["i"]
        
    cpn.apply_to_file(arguments['c'], input_file, arguments['o'],zipped, arguments['of'],
                    arguments['rn'], arguments['an'], arguments['r'], overwrite_ok)

if __name__ == "__main__":
    main()
