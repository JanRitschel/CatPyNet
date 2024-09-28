import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from catpynet.fileIO.IOManager import OUTPUT_FILE_FORMATS, TRUTH_STRINGS
from catpynet.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from catpynet.algorithm.MinRAFGeneratingElement import MinRAFGeneratingElement
from tqdm import tqdm
import catpynet.main.CatPyNet as cpn
import argparse


#__version__ = importlib.metadata.version('catPyNet')

def main():

    parser = argparse.ArgumentParser(
        description="Performs Max RAF and other computations")
    
#    parser.add_argument("--version", action="version", version='%(prog)s ' + __version__)
    parser.add_argument("-c", metavar="compute", required=True,
                        help="The computation to perform from: " + str(cpn.ALL_ALGORITHMS), 
                        choices=cpn.ALL_ALGORITHMS)
    parser.add_argument("-i", metavar="input",
                        help="Input file (stdin ok)", default="stdin")
    parser.add_argument("-o", metavar='output_file',
                        help="Output file (stdout ok)", default="stdout")
    parser.add_argument("-z", metavar='output zipped',
                        help="Should the output be a zipped directory. (True or False)", 
                        choices=TRUTH_STRINGS, 
                        default="False")
    parser.add_argument("-of", metavar="output format",
                        help="file format to be written. e.g. '.crs'", 
                        choices=OUTPUT_FILE_FORMATS, 
                        default=None)
    parser.add_argument("-rn", metavar="reaction notation",
                        help="Output reaction notation", default="FULL")
    parser.add_argument("-an", metavar="arrow notation",
                        help="Output arrow notation", default="USES_EQUALS")
    parser.add_argument("-r", metavar="runs", help="Number of randomized runs for " +
                        MinIRAFHeuristic().name + " heuristic")
    parser.add_argument("-t", metavar="target molecule", help="Target Molecule for " +
                        MinRAFGeneratingElement().name, default="")
    parser.add_argument("-ow", metavar="overwrite ok", help="Sets if the program is allowed to " +
                        "write over files", choices=TRUTH_STRINGS, default="False")

    arguments = vars(parser.parse_args())
    zipped = True if arguments['z'].casefold() in ['True'.casefold(), "1"] else False
    overwrite_ok = True if arguments['ow'].casefold() in ['True'.casefold(), "1"] else False
    if arguments["i"] == 'stdin': 
        input_file = input("Please enter the file path you want to read from:")
    else:
        input_file = arguments["i"]
    if "," in arguments["t"]:
        target_molecules = arguments["t"].split(",")
    else:
        target_molecules = [arguments["t"]]
    
    if os.path.isdir(input_file):
        cpn.apply_algorithm_to_directory(arguments['c'], input_file, arguments['o'],zipped, arguments['of'],
                        arguments['rn'], arguments['an'], arguments['r'], target_molecules, 
                        overwrite_ok, time_dict={})
    elif os.path.isfile(input_file):
        cpn.apply_algorithm_to_file(arguments['c'], input_file, arguments['o'],zipped, arguments['of'],
                        arguments['rn'], arguments['an'], arguments['r'], target_molecules, 
                        overwrite_ok)
    else:
        raise IOError("Please select an existing file or directory as input.\n"
                      + "You tried to select: " + input_file)

if __name__ == "__main__":
    main()
