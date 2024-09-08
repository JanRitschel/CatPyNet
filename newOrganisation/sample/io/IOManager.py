from sample.model.ReactionSystem import ReactionSystem
from sample.settings.ReactionNotation import ReactionNotation
from sample.settings.ArrowNotation import ArrowNotation
from sample.algorithm.AlgorithmBase import AlgorithmBase
from sample.io.GraphIO import write, SUPPORTED_GRAPH_FILE_FORMATS
from sample.io.ModelIO import ModelIO, SUPPORTED_FILE_FORMATS
import shutil
from tqdm import tqdm

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


ALL_FILE_FORMATS = SUPPORTED_FILE_FORMATS
ALL_FILE_FORMATS.extend(SUPPORTED_GRAPH_FILE_FORMATS)
ALL_FILE_FORMATS.extend([format.casefold() for format in ALL_FILE_FORMATS])
ALL_FILE_FORMATS.append(None)


def redirect_to_writer(output_systems:list[ReactionSystem],
                       output_path:str ="stdout",
                       output_format:str|None = None,
                       zipped:bool = False, 
                       reaction_notation:str = ReactionNotation.FULL,
                       arrow_notation:str = ArrowNotation.USES_EQUALS,
                       algorithm:AlgorithmBase|None = None):
    """Processes the inputs and redirects data to appropriate file writer.

    Args:
        output_systems (list[ReactionSystem]): reaction systems to be written as a file/files
        output_path (str, optional): path to generated file. Default stdout prints in terminal. Defaults to "stdout".
        output_format (str | None, optional): If given this determines the file format of the output. Defaults to None.
        zipped (bool, optional): should the resulting files be zipped to an archive. Defaults to False.
        reaction_notation (str, optional): For '.crs' files. Determines reaction notation format. Defaults to ReactionNotation.FULL.
        arrow_notation (str, optional): For '.crs' files. Determines arrow format. Defaults to ArrowNotation.USES_EQUALS.
        algorithm (AlgorithmBase | None, optional): only relevant for message generation. Defaults to None.
    """
    if output_format and output_path != "stdout":
        output_path = os.path.splitext(output_path)[0] + output_format
    elif not output_format and output_path != "stdout":
        output_format = os.path.splitext(output_path)[1]

    if zipped:
        output = os.path.split(os.path.abspath(output_path))
        output_directory = os.path.join(output[0], output[1].split(".")[0])
        output_file = output[1]
        output_path = os.path.join(output_directory, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if output_path != "stdout":
        tqdm.write("Writing file: " + output_path)

    if all(output_systems):
        if not any([rs.reactions for rs in output_systems]):
            tqdm.write("The resulting reaction systems have no reactions.\n"
                       + "No " + algorithm.NAME)
    if not any(output_systems):
        tqdm.write("The resulting reaction systems have no reactions.\n"
                       + "No " + algorithm.NAME)
        return
    
    if output_format in SUPPORTED_GRAPH_FILE_FORMATS:
        write(output_systems, output_path, output_format, algorithm)
    elif output_format == ".crs":
        with open(output_path, "w") as f:
            res_str = ""
            for output_system in output_systems:
                if not output_system.reactions:
                    res_str += ("The resulting reaction system has no reactions.\n"
                        + "No " + algorithm.NAME)
                else:
                    tqdm.write(output_system.get_header_line())
                    res_str += ModelIO().write(output_system,
                                            True,
                                            reaction_notation,
                                            arrow_notation)
                res_str += "\n"
            f.write(res_str)
    elif output_path == "stdout":
        res_str = ""
        for output_system in output_systems:
            if not output_system.reactions:
                res_str += ("The resulting reaction system has no reactions.\n"
                       + "No " + algorithm.NAME)
            else:
                tqdm.write(output_system.get_header_line())
                res_str += ModelIO().write(output_system,
                                        True,
                                        reaction_notation,
                                        arrow_notation)
            res_str += "\n"
        print(res_str)
    else:
        tqdm.write("Given output file format was not recognized.\n" +
                   ".crs is assumed.")
        output_path = output_path.split(".")[0] + ".crs"
        for output_system in output_systems:
            with open(output_path, "w") as f:
                res_str = ""
                if not output_system.reactions:
                        res_str += ("The resulting reaction system has no reactions.\n"
                            + "No " + algorithm.NAME)
                else:
                    tqdm.write(output_system.get_header_line())
                    res_str += ModelIO().write(output_system,
                                            True,
                                            reaction_notation,
                                            arrow_notation)
                res_str += "\n"
                f.write(res_str)

    if zipped == "True":
        shutil.make_archive(output_directory, 'zip', output_directory)
        if os.path.isdir(output_directory):
            shutil.rmtree(output_directory)
        tqdm.write("made zip")
    