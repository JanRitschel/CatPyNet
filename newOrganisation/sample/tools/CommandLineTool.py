from sample.io.IOManager import ALL_FILE_FORMATS
from _version import __version__, AUTHOR
from sample.algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from tqdm import tqdm
import sample.main.CatPyNet as cpn
import argparse

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def main():

    parser = argparse.ArgumentParser(
        description="Performs Max RAF and other computations")

    # ZU MACHEN, __version__snummer muss ordnetlich geklärt werden
    parser.add_argument("--version", action="version", version='%(prog)s ' + __version__)
    parser.add_argument("--license", action="store_true")
    parser.add_argument("--authors", action="store_true")
    parser.add_argument("-c", metavar="compute", required=True,
                        help="The computation to perform", choices=cpn.ALL_ALGORITHMS)
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
    
    if arguments["-license"]:
        tqdm.write("Copyright (C) 2023. GPL 3. This program comes with ABSOLUTELY NO WARRANTY.")  # ZU MACHEN, License muss richtige sein)
    if arguments['-author']:
        tqdm.write(AUTHOR)
        
    cpn.run_on_file(arguments['c'], arguments['i'], arguments['o'],arguments['z'], arguments['of'],
                    arguments['rn'], arguments['an'], arguments['r'])

if __name__ == "__main__":
    main()
