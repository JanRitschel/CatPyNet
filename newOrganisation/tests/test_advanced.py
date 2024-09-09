# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sample.io.IOManager import ALL_FILE_FORMATS
from sample.settings.ReactionNotation import ReactionNotation, ArrowNotation
import sample.tools.CommandLineTool as clt
import sample.main.CatPyNet as cpn
from sample.algorithm.AlgorithmBase import AlgorithmBase
from os import listdir
from os.path import isfile, join
from tqdm import tqdm


if __name__ == '__main__':
    
    algos = AlgorithmBase.list_all_algorithms()
    mypath = "G:\\Github\\BA-Jan\\newOrganisation\\test_files"
    respath = "D:\\Users\\jrls2_000\\Documents\\UNI\\_BA\\test_data_results"
    test_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    
    algos.remove("iRAF")
    algos = ["iRAF"]
    total_test_files = (len(algos) * 2 * len(ALL_FILE_FORMATS) * len(ReactionNotation) 
                        * len(ArrowNotation) * len(test_files))
    with tqdm(desc="Total Test Files:", total=total_test_files) as tot_f:
        for algo in algos:
            for zipped in [True, False]:
                for output_format in ALL_FILE_FORMATS:
                    for reaction_notation in ReactionNotation:
                        for arrow_notation in ArrowNotation:
                            if not output_format: continue
                            output_addition = os.path.join(algo, 
                                                        str(zipped), 
                                                        output_format.removeprefix("."), 
                                                        reaction_notation.value,
                                                        arrow_notation.value)
                            
                            output_path = os.path.join(respath, output_addition)
                            
                            cpn.apply_to_directory(algo,
                                                mypath,
                                                output_path,
                                                zipped,
                                                output_format,
                                                reaction_notation,
                                                arrow_notation,
                                                100,
                                                True)
                            
                            tot_f.update(len(test_files))
                        
    
    """ for algo in algos:
        if algo=="iRAF":continue
        algo_respath = respath + "\\" + algo
        for j, file in enumerate(test_files):
            if j == 14: continue
            sys.argv.append("-c")
            sys.argv.append(algo)
            sys.argv.append("-z")
            sys.argv.append("False")
            sys.argv.append("-of")
            sys.argv.append(".crs")
            sys.argv.append("-i")
            sys.argv.append(mypath + "\\"+ file)
            sys.argv.append("-o")
            full_file = algo_respath + "\\" + "result-" + file
            os.makedirs(os.path.dirname(full_file), exist_ok=True)
            sys.argv.append(full_file)
            clt.main()
            for i in range(1, len(sys.argv)):
                del sys.argv[1]
            gc.collect() """
    
    print([[chr(v) for v in range(ord('a'), ord('a') + 26)]])
