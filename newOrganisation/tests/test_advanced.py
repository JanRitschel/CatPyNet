# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sample.model import Reaction
import hypothesis.extra.ghostwriter as ghostwriter
import sample.main.CommandLineTool as clt
from sample.algorithm.AlgorithmBase import AlgorithmBase
from os import listdir
from os.path import isfile, join


if __name__ == '__main__':
    
    algos = AlgorithmBase.list_all_algorithms()
    mypath = "G:\\Github\\BA-Jan\\newOrganisation\\test_files"
    respath = "G:\\Github\\BA-Jan\\newOrganisation\\test_results"
    test_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    
    for algo in algos:
        algo_respath = respath + "\\" + algo
        for j, file in enumerate(test_files):
            if j == 12: continue
            sys.argv.append("-c")
            sys.argv.append(algo)
            sys.argv.append("-i")
            sys.argv.append(mypath + "\\"+ file)
            sys.argv.append("-o")
            full_file = algo_respath + "\\" + "result-" + file
            os.makedirs(os.path.dirname(full_file), exist_ok=True)
            sys.argv.append(full_file)
            clt.main()
    
    print([[chr(v) for v in range(ord('a'), ord('a') + 26)]])
