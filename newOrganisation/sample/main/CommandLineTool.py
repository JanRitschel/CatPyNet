import argparse

from ..algorithm.AlgorithmBase import AlgorithmBase
from ..algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from ..io.ModelIO import ModelIO

def main():

    all_algorithms = AlgorithmBase.list_all_algorithms()
    
    parser = argparse.ArgumentParser(description=
                                     "Performs Max RAF and other computations")
    
    parser.add_argument("--version", action="version", version='%(prog)s 1.0') #ZU MACHEN, Versionsnummer muss ordnetlich geklärt werden
    parser.add_argument("--license", action="store_const", 
                        const="Copyright (C) 2023. GPL 3. This program comes with ABSOLUTELY NO WARRANTY.") #ZU MACHEN, License muss richtige sein
    parser.add_argument("--license", action="store_const", 
                        const="Daniel H. Huson and Mike Steel.") #ZU MACHEN, Autoren müssen richtige sein
    parser.add_argument("-c", metavar="compute", required=True, help="The computation to perform", choices= all_algorithms)
    parser.add_argument("-i", metavar="input", help="Input file (stdin ok)", default="stdin") #UNKLAR, soll der file so heißen oder wird etwas spezifisches aufgerufen
    parser.add_argument("-o", metavar="output", help="Output file (stdout ok)", default="stdout")
    parser.add_argument("-rn", metavar="reaction_notation", help="Output reaction notation") #ZU MACHEN, Reaction Notation class
    parser.add_argument("-an", metavar="arrow_notation", help="Output arrow notation") #ZU MACHEN, Arrow Notation class
    parser.add_argument("-r", metavar="runs", help= "Number of randomized runs for " + MinIRAFHeuristic.name + " heuristic")
    parser.add_argument("-p", metavar="properties_file", default="") #ZU MACHEN, Default File muss erstellt werden

    #ZU MACHEN, comment argument (?) mit OTHER variable aus ArgsOptions
    arguments = vars(parser.parse_args())

    #ZU MACHEN, Files auf verschiedenheit, schreibbarkeit und existenz prüfen
    input_system = arguments['input'] #ZU MACHEN, file organisation/wie schreibt java hier rein?
    algorithm:AlgorithmBase = AlgorithmBase.get_algorithm_by_name(arguments['compute'])
    if isinstance(algorithm, MinIRAFHeuristic):
        irr_raf_heuristic = MinIRAFHeuristic()
        irr_raf_heuristic.number_of_random_insertion_orders = arguments['runs']
        output_systems = irr_raf_heuristic.apply_all_smallest(input_system)
        if arguments['output'] != "stdout":  #ZU MACHEN, wieder std stuff
            print("Writing file: " + arguments['output'])
        try:
            w = "foo" #ZU MACHEN, writer je nach zip/gzip oder normal abhängig von output_file
            for output_system in output_systems:
                ModelIO.write(output_system, w, arguments['reaction_notation'], arguments['arrow_notation'], include_food = True) #ZU MACHEN, ModelIO
                w.write("\n")
        except: #UNKLAR, braucht es überhaupt ein try statement?
            pass
    else:
        output_system = algorithm.apply(input_system)
        if arguments['output'] != "stdout":  #ZU MACHEN, wieder std stuff
            print("Writing file: " + arguments['output'])
        try:
            w = "foo" #ZU MACHEN, writer je nach zip/gzip oder normal abhängig von output_file
            ModelIO.write(output_system, w, arguments['reaction_notation'], arguments['arrow_notation'], include_food = True) #ZU MACHEN, ModelIO
        except: #UNKLAR, braucht es überhaupt ein try statement?
            pass

def parse_input_file(file_name:str):

    #ZU MACHEN, ImportWimsFormat, ReactionNotation.detectNotation, Abhängig davon readstyle
    return

if __name__ == "__main__":
    main()